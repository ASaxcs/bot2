"""
Dialogue Triggers for Emotional Processing
Handles emotional triggers from user dialogue and conversation patterns
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from state_manager import EmotionType

class DialogueTriggers:
    """Processes dialogue for emotional triggers and patterns"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Trigger sensitivity from config
        self.sensitivity = config.get("emotion", {}).get("sensitivity", 0.6)
        self.trigger_thresholds = config.get("emotion", {}).get("trigger_thresholds", {
            "joy": 0.7,
            "sadness": 0.6,
            "anger": 0.8,
            "fear": 0.7,
            "surprise": 0.6
        })
        
        # Initialize trigger patterns
        self._init_trigger_patterns()
    
    def _init_trigger_patterns(self):
        """Initialize emotional trigger patterns"""
        self.trigger_patterns = {
            "joy": {
                "keywords": [
                    "happy", "joy", "joyful", "excited", "thrilled", "delighted",
                    "wonderful", "amazing", "fantastic", "great", "excellent",
                    "love", "adore", "cherish", "celebrate", "triumph", "success",
                    "perfect", "beautiful", "awesome", "brilliant", "marvelous"
                ],
                "phrases": [
                    "i'm so happy", "this is great", "i love this", "fantastic news",
                    "couldn't be better", "over the moon", "on cloud nine",
                    "best day ever", "so excited", "absolutely wonderful"
                ],
                "patterns": [
                    r"(\w+)?\s*(love|adore|enjoy)\s+(\w+)",
                    r"(so|very|extremely)\s+(happy|excited|thrilled)",
                    r"(this|that)\s+is\s+(amazing|wonderful|fantastic|great)"
                ]
            },
            
            "sadness": {
                "keywords": [
                    "sad", "depressed", "upset", "disappointed", "heartbroken",
                    "miserable", "gloomy", "melancholy", "dejected", "downhearted",
                    "grief", "sorrow", "despair", "lonely", "isolated",
                    "terrible", "awful", "horrible", "devastating", "tragic"
                ],
                "phrases": [
                    "i'm so sad", "feeling down", "really upset", "heartbroken",
                    "can't stop crying", "feeling lonely", "so disappointed",
                    "this is awful", "terrible news", "worst day ever"
                ],
                "patterns": [
                    r"(feel|feeling)\s+(sad|down|depressed|upset)",
                    r"(so|very|extremely)\s+(disappointed|upset|heartbroken)",
                    r"(can't|cannot)\s+(stop|help)\s+(crying|feeling sad)"
                ]
            },
            
            "anger": {
                "keywords": [
                    "angry", "furious", "mad", "rage", "livid", "irate",
                    "annoyed", "irritated", "frustrated", "outraged", "indignant",
                    "hate", "despise", "loathe", "detest", "resent",
                    "stupid", "idiotic", "ridiculous", "absurd", "unfair"
                ],
                "phrases": [
                    "so angry", "really mad", "can't believe", "absolutely furious",
                    "this is ridiculous", "makes me angry", "fed up with",
                    "sick and tired", "drives me crazy", "absolutely hate"
                ],
                "patterns": [
                    r"(so|really|extremely)\s+(angry|mad|furious|frustrated)",
                    r"(hate|despise|can't stand)\s+(\w+)",
                    r"(this|that)\s+is\s+(ridiculous|stupid|unfair|absurd)"
                ]
            },
            
            "fear": {
                "keywords": [
                    "afraid", "scared", "frightened", "terrified", "fearful",
                    "anxious", "worried", "nervous", "concerned", "panicked",
                    "dread", "apprehensive", "uneasy", "paranoid", "phobic",
                    "dangerous", "threatening", "risky", "unsafe", "precarious"
                ],
                "phrases": [
                    "i'm scared", "really worried", "so afraid", "terrified of",
                    "makes me nervous", "afraid that", "worried about",
                    "scared to death", "anxiety attack", "panic attack"
                ],
                "patterns": [
                    r"(scared|afraid|terrified)\s+(of|that|to)",
                    r"(really|so|very)\s+(worried|anxious|nervous)",
                    r"(what if|suppose)\s+(\w+)"
                ]
            },
            
            "surprise": {
                "keywords": [
                    "surprised", "shocked", "amazed", "astonished", "stunned",
                    "bewildered", "confused", "puzzled", "perplexed", "baffled",
                    "unexpected", "sudden", "abrupt", "unforeseen", "startling",
                    "wow", "whoa", "omg", "unbelievable", "incredible"
                ],
                "phrases": [
                    "can't believe", "so surprised", "didn't expect", "out of nowhere",
                    "caught off guard", "totally shocked", "never saw coming",
                    "what a surprise", "how unexpected", "didn't see that coming"
                ],
                "patterns": [
                    r"(can't|cannot)\s+believe",
                    r"(didn't|never)\s+(expect|think|imagine)",
                    r"(so|really|totally)\s+(surprised|shocked|amazed)"
                ]
            }
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            "very": 1.3,
            "extremely": 1.5,
            "really": 1.2,
            "so": 1.2,
            "absolutely": 1.4,
            "totally": 1.3,
            "completely": 1.4,
            "incredibly": 1.3,
            "tremendously": 1.4,
            "immensely": 1.3
        }
        
        # Negation words that can flip emotions
        self.negation_words = [
            "not", "never", "no", "none", "nothing", "nobody", "nowhere",
            "neither", "nor", "barely", "hardly", "scarcely", "seldom"
        ]
    
    def process_triggers(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process text for emotional triggers"""
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Detect emotions and their intensities
            emotion_scores = self._detect_emotions(cleaned_text)
            
            # Apply context if available
            if context:
                emotion_scores = self._apply_context(emotion_scores, context)
            
            # Determine dominant emotion
            dominant_emotion = self._get_dominant_emotion(emotion_scores)
            
            # Calculate overall emotional intensity
            intensity = self._calculate_intensity(emotion_scores)
            
            result = {
                "dominant_emotion": dominant_emotion,
                "emotion_scores": emotion_scores,
                "intensity": intensity,
                "timestamp": datetime.now().isoformat(),
                "trigger_details": self._get_trigger_details(cleaned_text, emotion_scores)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Trigger processing error: {e}")
            return {
                "dominant_emotion": "neutral",
                "emotion_scores": {"neutral": 1.0},
                "intensity": 0.0,
                "error": str(e)
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', text)
        
        return text
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions and calculate scores"""
        emotion_scores = {}
        
        for emotion, patterns in self.trigger_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in text:
                    # Check for negation
                    if self._is_negated(text, keyword):
                        score -= 0.3  # Reduce score for negated emotions
                    else:
                        score += 0.5
            
            # Check phrases
            for phrase in patterns["phrases"]:
                if phrase in text:
                    if self._is_negated(text, phrase):
                        score -= 0.4
                    else:
                        score += 0.7
            
            # Check regex patterns
            for pattern in patterns["patterns"]:
                matches = re.findall(pattern, text)
                if matches:
                    score += len(matches) * 0.6
            
            # Apply intensity modifiers
            score = self._apply_intensity_modifiers(text, score)
            
            # Normalize score
            emotion_scores[emotion] = max(0.0, min(1.0, score))
        
        # Add neutral baseline
        if not any(score > 0.1 for score in emotion_scores.values()):
            emotion_scores["neutral"] = 1.0
        
        return emotion_scores
    
    def _is_negated(self, text: str, target: str) -> bool:
        """Check if a target word/phrase is negated"""
        target_pos = text.find(target)
        if target_pos == -1:
            return False
        
        # Look for negation words before the target (within 5 words)
        prefix = text[:target_pos].split()[-5:]
        
        return any(neg_word in prefix for neg_word in self.negation_words)
    
    def _apply_intensity_modifiers(self, text: str, base_score: float) -> float:
        """Apply intensity modifiers to emotion scores"""
        words = text.split()
        modifier_factor = 1.0
        
        for word in words:
            if word in self.intensity_modifiers:
                modifier_factor *= self.intensity_modifiers[word]
        
        return base_score * modifier_factor
    
    def _apply_context(self, emotion_scores: Dict[str, float], context: Dict) -> Dict[str, float]:
        """Apply contextual information to emotion scores"""
        # This could include conversation history, user personality, etc.
        # For now, we'll implement basic context sensitivity
        
        context_factor = context.get("emotional_context_factor", 1.0)
        
        # Apply context factor
        for emotion in emotion_scores:
            emotion_scores[emotion] *= context_factor
        
        return emotion_scores
    
    def _get_dominant_emotion(self, emotion_scores: Dict[str, float]) -> str:
        """Get the dominant emotion from scores"""
        if not emotion_scores:
            return "neutral"
        
        # Find emotion with highest score above threshold
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        if max_emotion[1] >= self.trigger_thresholds.get(max_emotion[0], 0.5):
            return max_emotion[0]
        else:
            return "neutral"
    
    def _calculate_intensity(self, emotion_scores: Dict[str, float]) -> float:
        """Calculate overall emotional intensity"""
        if not emotion_scores:
            return 0.0
        
        # Use the maximum score as intensity
        max_score = max(emotion_scores.values())
        
        # Apply sensitivity adjustment
        adjusted_intensity = max_score * self.sensitivity
        
        return min(1.0, adjusted_intensity)
    
    def _get_trigger_details(self, text: str, emotion_scores: Dict[str, float]) -> Dict[str, Any]:
        """Get detailed information about what triggered the emotions"""
        details = {
            "triggered_keywords": [],
            "triggered_phrases": [],
            "pattern_matches": [],
            "negations_detected": [],
            "intensity_modifiers": []
        }
        
        # Find what triggered each emotion
        for emotion, score in emotion_scores.items():
            if score > 0.1 and emotion in self.trigger_patterns:
                patterns = self.trigger_patterns[emotion]
                
                # Find triggered keywords
                for keyword in patterns["keywords"]:
                    if keyword in text:
                        details["triggered_keywords"].append({
                            "emotion": emotion,
                            "keyword": keyword,
                            "negated": self._is_negated(text, keyword)
                        })
                
                # Find triggered phrases
                for phrase in patterns["phrases"]:
                    if phrase in text:
                        details["triggered_phrases"].append({
                            "emotion": emotion,
                            "phrase": phrase,
                            "negated": self._is_negated(text, phrase)
                        })
        
        # Find intensity modifiers
        words = text.split()
        for word in words:
            if word in self.intensity_modifiers:
                details["intensity_modifiers"].append({
                    "word": word,
                    "factor": self.intensity_modifiers[word]
                })
        
        return details
    
    def get_emotion_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent emotion detection history"""
        # This would typically be stored and retrieved from memory
        # For now, return empty list as placeholder
        return []
    
    def update_trigger_patterns(self, new_patterns: Dict[str, Any]) -> bool:
        """Update trigger patterns dynamically"""
        try:
            for emotion, patterns in new_patterns.items():
                if emotion in self.trigger_patterns:
                    self.trigger_patterns[emotion].update(patterns)
                else:
                    self.trigger_patterns[emotion] = patterns
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pattern update error: {e}")
            return False
