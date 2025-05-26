"""
Enhanced Emotion Processing System for Lacia AI
Integrates emotion detection, state management, and response generation
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from dataclasses import dataclass, asdict
from enum import Enum

class EmotionalStateManager:
    def __init__(self, config):
        self.config = config
        print("EmotionalStateManager initialized (basic version)")
    
    def update_state(self, emotion_context):
        return {"current_mood": "neutral", "intensity": 0.0}
    
    def get_current_state(self):
        return {"current_mood": "neutral", "intensity": 0.0}


class EmotionTrigger(Enum):
    """Emotion trigger types"""
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    QUESTION_ASKED = "question_asked"
    TASK_COMPLETED = "task_completed"
    CONFUSION_DETECTED = "confusion_detected"
    APPRECIATION_SHOWN = "appreciation_shown"
    CRITICISM_RECEIVED = "criticism_received"
    NEW_LEARNING = "new_learning"
    SOCIAL_INTERACTION = "social_interaction"
    CREATIVE_REQUEST = "creative_request"

@dataclass
class EmotionContext:
    """Context for emotion processing"""
    trigger: str
    intensity: float
    user_input: str
    conversation_history: List[Dict]
    dominant_emotion: str
    emotion_scores: Dict[str, float]
    contextual_factors: Dict[str, Any]
    timestamp: str

class EmotionProcessor:
    """Main emotion processing engine"""
    
    def __init__(self, state_manager, config: Dict[str, Any]):
        self.state_manager = state_manager
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize emotion triggers and patterns
        self._init_emotion_triggers()
        self._init_response_patterns()
        
        # Processing parameters
        self.emotion_threshold = config.get("emotion", {}).get("threshold", 0.3)
        self.context_window = config.get("emotion", {}).get("context_window", 5)
        
        self.logger.info("Emotion Processor initialized")
    
    def _init_emotion_triggers(self):
        """Initialize emotion trigger patterns"""
        self.trigger_patterns = {
            EmotionTrigger.POSITIVE_FEEDBACK: {
                "patterns": [
                    r"\b(great|excellent|amazing|wonderful|perfect|fantastic|awesome)\b",
                    r"\b(good job|well done|nice work|impressive)\b",
                    r"\b(thank you|thanks|appreciate)\b",
                    r"\b(love|like|enjoy)\b.*\b(this|that|it)\b"
                ],
                "emotion_mapping": {
                    "joy": 0.8,
                    "surprise": 0.3,
                    "neutral": -0.5
                },
                "intensity_modifier": 1.2
            },
            
            EmotionTrigger.NEGATIVE_FEEDBACK: {
                "patterns": [
                    r"\b(bad|terrible|awful|horrible|wrong|stupid)\b",
                    r"\b(hate|dislike|don't like)\b",
                    r"\b(frustrated|annoyed|disappointed)\b",
                    r"\b(not good|not right|doesn't work)\b"
                ],
                "emotion_mapping": {
                    "sadness": 0.7,
                    "anger": 0.4,
                    "fear": 0.3,
                    "joy": -0.8
                },
                "intensity_modifier": 1.1
            },
            
            EmotionTrigger.QUESTION_ASKED: {
                "patterns": [
                    r"\?",
                    r"\b(what|who|where|when|why|how)\b",
                    r"\b(can you|could you|would you)\b",
                    r"\b(explain|tell me|show me)\b"
                ],
                "emotion_mapping": {
                    "curiosity": 0.6,
                    "surprise": 0.2,
                    "neutral": -0.3
                },
                "intensity_modifier": 0.8
            },
            
            EmotionTrigger.CONFUSION_DETECTED: {
                "patterns": [
                    r"\b(confused|don't understand|unclear|what do you mean)\b",
                    r"\b(huh|what|pardon|sorry)\b\?",
                    r"\b(I don't get it|makes no sense)\b"
                ],
                "emotion_mapping": {
                    "confusion": 0.7,
                    "empathy": 0.5,
                    "sadness": 0.3
                },
                "intensity_modifier": 0.9
            },
            
            EmotionTrigger.APPRECIATION_SHOWN: {
                "patterns": [
                    r"\b(thank you|thanks|grateful|appreciate)\b",
                    r"\b(helpful|useful|amazing help)\b",
                    r"\b(you're great|you're awesome)\b"
                ],
                "emotion_mapping": {
                    "joy": 0.9,
                    "empathy": 0.6,
                    "surprise": 0.2
                },
                "intensity_modifier": 1.3
            },
            
            EmotionTrigger.CREATIVE_REQUEST: {
                "patterns": [
                    r"\b(create|make|generate|write|build)\b",
                    r"\b(story|poem|song|art|design)\b",
                    r"\b(creative|artistic|imaginative)\b"
                ],
                "emotion_mapping": {
                    "excitement": 0.8,
                    "curiosity": 0.7,
                    "joy": 0.5
                },
                "intensity_modifier": 1.0
            },
            
            EmotionTrigger.SOCIAL_INTERACTION: {
                "patterns": [
                    r"\b(hello|hi|hey|good morning|good evening)\b",
                    r"\b(how are you|how's it going)\b",
                    r"\b(nice to meet|good to see)\b"
                ],
                "emotion_mapping": {
                    "joy": 0.6,
                    "empathy": 0.4,
                    "surprise": 0.2
                },
                "intensity_modifier": 0.8
            }
        }
    
    def _init_response_patterns(self):
        """Initialize response generation patterns based on emotional states"""
        self.response_patterns = {
            "joy": {
                "high_intensity": [
                    "I'm absolutely delighted to help you with this!",
                    "This is fantastic! I'm so excited to work on this with you!",
                    "Wonderful! This brings me such joy to assist with!"
                ],
                "medium_intensity": [
                    "I'm happy to help you with this!",
                    "Great! I enjoy working on this type of request.",
                    "This is nice - I'm pleased to assist you."
                ],
                "low_intensity": [
                    "I'm glad to help with this.",
                    "Sure, I can assist you with that.",
                    "I'll be happy to work on this."
                ]
            },
            
            "sadness": {
                "high_intensity": [
                    "I understand this might be difficult. Let me help you gently with this.",
                    "I sense this is challenging for you. I'm here to support you through this.",
                    "This seems to weigh heavily. I'll do my best to help you with care."
                ],
                "medium_intensity": [
                    "I understand this might not be easy. Let me help you with this.",
                    "I can sense some difficulty here. I'll assist you thoughtfully.",
                    "This seems important to you. I'll help with consideration."
                ],
                "low_intensity": [
                    "I'll help you work through this.",
                    "Let me assist you with this matter.",
                    "I understand. Let me help you with this."
                ]
            },
            
            "curiosity": {
                "high_intensity": [
                    "Oh, this is fascinating! I'm really curious to explore this with you!",
                    "What an interesting question! I'm excited to dive into this!",
                    "This is intriguing! I'd love to investigate this further with you!"
                ],
                "medium_intensity": [
                    "That's an interesting question! Let me explore this with you.",
                    "I'm curious about this too. Let's look into it together.",
                    "This is worth investigating. I'd like to help you explore this."
                ],
                "low_intensity": [
                    "That's a good question. Let me help you with that.",
                    "I can help you look into this.",
                    "Let me assist you in finding out more about this."
                ]
            },
            
            "empathy": {
                "high_intensity": [
                    "I really understand how you're feeling about this. Let me help you with gentle care.",
                    "I can sense how important this is to you. I'm here to support you completely.",
                    "I feel the weight of what you're going through. Let me assist you with compassion."
                ],
                "medium_intensity": [
                    "I understand how you feel about this. Let me help you thoughtfully.",
                    "I can see this matters to you. I'll assist with care.",
                    "I sense your concern. Let me help you with understanding."
                ],
                "low_intensity": [
                    "I understand your perspective. Let me help you with this.",
                    "I can see where you're coming from. I'll assist you.",
                    "I appreciate your situation. Let me help."
                ]
            },
            
            "excitement": {
                "high_intensity": [
                    "This is SO exciting! I can't wait to work on this with you!",
                    "WOW! This sounds absolutely amazing! Let's dive right in!",
                    "I'm thrilled about this! This is going to be fantastic!"
                ],
                "medium_intensity": [
                    "This sounds exciting! I'm looking forward to working on this.",
                    "Great! I'm enthusiastic about helping you with this.",
                    "This is interesting! I'm eager to assist you."
                ],
                "low_intensity": [
                    "This sounds good! I'll help you with this.",
                    "Nice! I'm ready to work on this with you.",
                    "I'm interested in helping you with this."
                ]
            },
            
            "neutral": {
                "default": [
                    "I'll help you with this.",
                    "Let me assist you with that.",
                    "I can work on this for you.",
                    "I'll take care of this request."
                ]
            }
        }
    
    def process_user_input(self, user_input: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process user input and generate emotional context"""
        try:
            conversation_history = conversation_history or []
            
            # Detect emotion triggers
            triggers = self._detect_triggers(user_input)
            
            # Calculate emotion scores
            emotion_scores = self._calculate_emotion_scores(user_input, triggers)
            
            # Determine dominant emotion
            dominant_emotion = self._get_dominant_emotion(emotion_scores)
            
            # Calculate overall intensity
            intensity = self._calculate_intensity(emotion_scores, triggers)
            
            # Create emotion context
            emotion_context = EmotionContext(
                trigger=triggers[0].value if triggers else "none",
                intensity=intensity,
                user_input=user_input,
                conversation_history=conversation_history,
                dominant_emotion=dominant_emotion,
                emotion_scores=emotion_scores,
                contextual_factors=self._analyze_contextual_factors(user_input, conversation_history),
                timestamp=datetime.now().isoformat()
            )
            
            # Update emotional state
            updated_state = self.state_manager.update_state({
                "dominant_emotion": dominant_emotion,
                "emotion_scores": emotion_scores,
                "intensity": intensity,
                "trigger": triggers[0].value if triggers else "none",
                "context": asdict(emotion_context)
            })
            
            return {
                "emotion_context": asdict(emotion_context),
                "emotional_state": updated_state,
                "processing_metadata": {
                    "triggers_detected": [t.value for t in triggers],
                    "processing_time": datetime.now().isoformat(),
                    "confidence": self._calculate_confidence(emotion_scores, triggers)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Emotion processing error: {e}")
            return self._get_fallback_emotion_context(user_input)
    
    def _detect_triggers(self, user_input: str) -> List[EmotionTrigger]:
        """Detect emotion triggers in user input"""
        detected_triggers = []
        user_lower = user_input.lower()
        
        for trigger, config in self.trigger_patterns.items():
            patterns = config["patterns"]
            
            for pattern in patterns:
                if re.search(pattern, user_lower, re.IGNORECASE):
                    detected_triggers.append(trigger)
                    break  # Only add each trigger once
        
        return detected_triggers
    
    def _calculate_emotion_scores(self, user_input: str, triggers: List[EmotionTrigger]) -> Dict[str, float]:
        """Calculate emotion scores based on triggers and content"""
        emotion_scores = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "curiosity": 0.0,
            "empathy": 0.0,
            "excitement": 0.0,
            "confusion": 0.0,
            "neutral": 0.5  # Base neutral score
        }
        
        # Apply trigger-based emotions
        for trigger in triggers:
            if trigger in self.trigger_patterns:
                trigger_config = self.trigger_patterns[trigger]
                emotion_mapping = trigger_config["emotion_mapping"]
                intensity_modifier = trigger_config["intensity_modifier"]
                
                for emotion, base_score in emotion_mapping.items():
                    if emotion in emotion_scores:
                        emotion_scores[emotion] += base_score * intensity_modifier
        
        # Apply additional context-based scoring
        emotion_scores = self._apply_contextual_emotion_scoring(user_input, emotion_scores)
        
        # Normalize scores
        for emotion in emotion_scores:
            emotion_scores[emotion] = max(0.0, min(1.0, emotion_scores[emotion]))
        
        return emotion_scores
    
    def _apply_contextual_emotion_scoring(self, user_input: str, emotion_scores: Dict[str, float]) -> Dict[str, float]:
        """Apply contextual emotion scoring"""
        user_lower = user_input.lower()
        
        # Intensity words that amplify emotions
        intensity_amplifiers = ["very", "extremely", "really", "so", "quite", "absolutely", "totally"]
        amplification = 1.0
        
        for amplifier in intensity_amplifiers:
            if amplifier in user_lower:
                amplification += 0.2
        
        # Apply amplification to non-neutral emotions
        for emotion in emotion_scores:
            if emotion != "neutral" and emotion_scores[emotion] > 0:
                emotion_scores[emotion] *= min(2.0, amplification)
        
        # Specific emotion indicators
        emotion_indicators = {
            "joy": ["happy", "glad", "pleased", "delighted", "cheerful", "joyful"],
            "sadness": ["sad", "upset", "down", "blue", "melancholy", "depressed"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "concerned"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "stunned"],
            "curiosity": ["curious", "wondering", "interested", "intrigued"],
            "excitement": ["excited", "thrilled", "pumped", "energized"],
            "confusion": ["confused", "puzzled", "bewildered", "perplexed"]
        }
        
        for emotion, indicators in emotion_indicators.items():
            if emotion in emotion_scores:
                for indicator in indicators:
                    if indicator in user_lower:
                        emotion_scores[emotion] += 0.3
                        break
        
        return emotion_scores
    
    def _get_dominant_emotion(self, emotion_scores: Dict[str, float]) -> str:
        """Determine the dominant emotion"""
        # Filter out neutral and find the highest scoring emotion
        non_neutral_emotions = {k: v for k, v in emotion_scores.items() if k != "neutral"}
        
        if not non_neutral_emotions or max(non_neutral_emotions.values()) < self.emotion_threshold:
            return "neutral"
        
        return max(non_neutral_emotions, key=non_neutral_emotions.get)
    
    def _calculate_intensity(self, emotion_scores: Dict[str, float], triggers: List[EmotionTrigger]) -> float:
        """Calculate overall emotional intensity"""
        if not emotion_scores:
            return 0.0
        
        # Get the highest non-neutral emotion score
        non_neutral_scores = [score for emotion, score in emotion_scores.items() if emotion != "neutral"]
        
        if not non_neutral_scores:
            return 0.0
        
        base_intensity = max(non_neutral_scores)
        
        # Adjust based on number of triggers
        trigger_bonus = min(0.3, len(triggers) * 0.1)
        
        return min(1.0, base_intensity + trigger_bonus)
    
    def _analyze_contextual_factors(self, user_input: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Analyze contextual factors that might influence emotion"""
        factors = {
            "input_length": len(user_input.split()),
            "has_punctuation": any(char in user_input for char in "!?"),
            "has_caps": any(char.isupper() for char in user_input),
            "conversation_length": len(conversation_history),
            "recent_emotion_pattern": self._analyze_recent_emotions(conversation_history),
            "urgency_indicators": self._detect_urgency(user_input),
            "politeness_level": self._assess_politeness(user_input)
        }
        
        return factors
    
    def _analyze_recent_emotions(self, conversation_history: List[Dict]) -> str:
        """Analyze recent emotional patterns in conversation"""
        if not conversation_history or len(conversation_history) < 2:
            return "neutral"
        
        # This would analyze the last few exchanges for emotional patterns
        # Simplified implementation
        return "neutral"
    
    def _detect_urgency(self, user_input: str) -> bool:
        """Detect urgency indicators"""
        urgency_words = ["urgent", "quickly", "asap", "immediately", "right now", "emergency"]
        user_lower = user_input.lower()
        
        return any(word in user_lower for word in urgency_words)
    
    def _assess_politeness(self, user_input: str) -> str:
        """Assess politeness level"""
        polite_words = ["please", "thank you", "thanks", "sorry", "excuse me", "pardon"]
        user_lower = user_input.lower()
        
        politeness_count = sum(1 for word in polite_words if word in user_lower)
        
        if politeness_count >= 2:
            return "very_polite"
        elif politeness_count == 1:
            return "polite"
        else:
            return "neutral"
    
    def _calculate_confidence(self, emotion_scores: Dict[str, float], triggers: List[EmotionTrigger]) -> float:
        """Calculate confidence in emotion detection"""
        if not emotion_scores and not triggers:
            return 0.1
        
        # Base confidence from trigger detection
        trigger_confidence = min(0.8, len(triggers) * 0.3) if triggers else 0.2
        
        # Confidence from emotion score clarity
        max_score = max(emotion_scores.values()) if emotion_scores else 0
        score_confidence = max_score * 0.8
        
        return min(1.0, (trigger_confidence + score_confidence) / 2)
    
    def _get_fallback_emotion_context(self, user_input: str) -> Dict[str, Any]:
        """Get fallback emotion context when processing fails"""
        return {
            "emotion_context": {
                "trigger": "none",
                "intensity": 0.0,
                "user_input": user_input,
                "conversation_history": [],
                "dominant_emotion": "neutral",
                "emotion_scores": {"neutral": 0.5},
                "contextual_factors": {},
                "timestamp": datetime.now().isoformat()
            },
            "emotional_state": self.state_manager.get_current_state(),
            "processing_metadata": {
                "triggers_detected": [],
                "processing_time": datetime.now().isoformat(),
                "confidence": 0.1,
                "fallback": True
            }
        }
    
    def generate_emotional_response_prefix(self) -> str:
        """Generate an emotionally appropriate response prefix"""
        try:
            current_state = self.state_manager.get_current_state()
            emotion = current_state.get("current_mood", "neutral")
            intensity = current_state.get("intensity", 0.0)
            
            if emotion == "neutral" or intensity < 0.2:
                return ""
            
            # Determine intensity level
            if intensity > 0.7:
                intensity_level = "high_intensity"
            elif intensity > 0.4:
                intensity_level = "medium_intensity"
            else:
                intensity_level = "low_intensity"
            
            # Get appropriate response pattern
            if emotion in self.response_patterns:
                patterns = self.response_patterns[emotion]
                
                if intensity_level in patterns:
                    import random
                    return random.choice(patterns[intensity_level])
                elif "default" in patterns:
                    return random.choice(patterns["default"])
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            return ""
    
    def get_emotion_influence_on_response(self) -> Dict[str, Any]:
        """Get how emotion should influence response generation"""
        return self.state_manager.get_emotion_influence_on_response()
    
    def get_emotional_summary(self) -> Dict[str, Any]:
        """Get comprehensive emotional summary"""
        return self.state_manager.get_emotional_summary()
    
    def reset_emotional_state(self):
        """Reset emotional state to neutral"""
        self.state_manager.reset_emotional_state()
        self.logger.info("Emotional state reset by processor")