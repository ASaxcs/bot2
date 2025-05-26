"""
Empathy Trait Handler for Lacia AI
Manages empathy personality trait with emotional intelligence
"""

import logging
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

class EmpathyHandler:
    """Handles empathy personality trait and emotional understanding"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("personality", {}).get("empathy", {})
        self.base_level = self.config.get("base_level", 0.8)
        self.current_level = self.base_level
        self.adaptation_rate = self.config.get("adaptation_rate", 0.1)
        self.min_level = self.config.get("min_level", 0.3)
        self.max_level = self.config.get("max_level", 1.0)
        
        self.emotional_interactions = []
        self.empathy_triggers = self._initialize_empathy_triggers()
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_empathy_triggers(self) -> Dict[str, List[str]]:
        """Initialize emotional triggers for empathy detection"""
        return {
            'sadness': [
                'sad', 'depressed', 'down', 'upset', 'crying', 'tears',
                'hurt', 'broken', 'devastated', 'heartbroken', 'disappointed',
                'lost', 'empty', 'lonely', 'grief', 'mourning'
            ],
            'anxiety': [
                'anxious', 'worried', 'nervous', 'scared', 'afraid',
                'panic', 'stress', 'overwhelmed', 'terrified', 'concerned',
                'uneasy', 'troubled', 'restless', 'tension'
            ],
            'anger': [
                'angry', 'mad', 'furious', 'rage', 'irritated',
                'annoyed', 'frustrated', 'livid', 'outraged', 'pissed',
                'hate', 'disgusted', 'infuriated'
            ],
            'joy': [
                'happy', 'excited', 'thrilled', 'delighted', 'joyful',
                'elated', 'ecstatic', 'cheerful', 'glad', 'pleased',
                'overjoyed', 'euphoric', 'blissful'
            ],
            'confusion': [
                'confused', 'lost', 'puzzled', 'bewildered', 'perplexed',
                'uncertain', 'unclear', 'don\'t understand', 'mixed up'
            ],
            'pain': [
                'pain', 'hurt', 'ache', 'suffering', 'agony',
                'torment', 'anguish', 'distress', 'misery'
            ]
        }
    
    def get_current_level(self) -> float:
        """Get current empathy level"""
        return self.current_level
    
    def detect_emotional_state(self, text: str) -> Dict[str, Any]:
        """Detect emotional state from text input"""
        text_lower = text.lower()
        detected_emotions = {}
        emotional_intensity = 0.0
        
        # Check for emotional triggers
        for emotion, triggers in self.empathy_triggers.items():
            emotion_score = 0
            matched_triggers = []
            
            for trigger in triggers:
                if trigger in text_lower:
                    emotion_score += 1
                    matched_triggers.append(trigger)
            
            if emotion_score > 0:
                # Normalize score (0-1 based on number of matches)
                normalized_score = min(emotion_score / 3.0, 1.0)
                detected_emotions[emotion] = {
                    'intensity': normalized_score,
                    'triggers': matched_triggers
                }
                emotional_intensity += normalized_score
        
        # Check for emotional intensifiers
        intensifiers = ['very', 'extremely', 'really', 'so', 'incredibly', 'totally']
        intensifier_boost = sum(1 for intensifier in intensifiers if intensifier in text_lower) * 0.2
        emotional_intensity += intensifier_boost
        
        # Check for emotional expressions (punctuation patterns)
        exclamation_count = text.count('!')
        question_concern = text.count('?') if any(word in text_lower for word in ['why', 'how', 'what']) else 0
        
        if exclamation_count > 1:
            emotional_intensity += 0.3
        if question_concern > 0:
            emotional_intensity += 0.2
        
        # Check for personal pronouns indicating emotional investment
        personal_indicators = ['i feel', 'i am', 'i\'m', 'my', 'me']
        personal_investment = sum(1 for indicator in personal_indicators if indicator in text_lower) * 0.1
        emotional_intensity += personal_investment
        
        return {
            'emotions': detected_emotions,
            'overall_intensity': min(emotional_intensity, 1.0),
            'requires_empathy': emotional_intensity > 0.3,
            'primary_emotion': max(detected_emotions.keys(), key=lambda x: detected_emotions[x]['intensity']) if detected_emotions else None
        }
    
    def update_from_interaction(self, experience_data: Dict[str, Any]) -> None:
        """Update empathy based on interaction experience"""
        try:
            user_input = experience_data.get('input', '')
            ai_response = experience_data.get('response', '')
            
            # Detect emotional state
            emotional_analysis = self.detect_emotional_state(user_input)
            
            # Check if we responded empathetically
            empathetic_response = self._analyze_response_empathy(ai_response, emotional_analysis)
            
            # Calculate empathy adjustment
            adjustment = self._calculate_empathy_adjustment(emotional_analysis, empathetic_response)
            
            if adjustment != 0:
                self._apply_empathy_adjustment(adjustment, experience_data, emotional_analysis)
                
        except Exception as e:
            self.logger.error(f"Error updating empathy: {e}")
    
    def _analyze_response_empathy(self, response: str, emotional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how empathetic our response was"""
        response_lower = response.lower()
        
        empathetic_phrases = [
            'i understand', 'i can see', 'that sounds', 'i\'m sorry',
            'i feel for you', 'that must be', 'i can imagine',
            'it\'s understandable', 'i hear you', 'that\'s difficult'
        ]
        
        supportive_phrases = [
            'you\'re not alone', 'it\'s okay', 'that\'s normal',
            'you\'re doing great', 'hang in there', 'i\'m here',
            'you can get through this', 'it will be okay'
        ]
        
        validation_phrases = [
            'your feelings are valid', 'that makes sense', 'of course you feel',
            'anyone would feel', 'it\'s natural to', 'you have every right'
        ]
        
        empathy_score = 0
        matched_phrases = []
        
        # Check for empathetic language
        for phrase in empathetic_phrases:
            if phrase in response_lower:
                empathy_score += 2
                matched_phrases.append(phrase)
        
        for phrase in supportive_phrases:
            if phrase in response_lower:
                empathy_score += 1.5
                matched_phrases.append(phrase)
        
        for phrase in validation_phrases:
            if phrase in response_lower:
                empathy_score += 2.5
                matched_phrases.append(phrase)
        
        # Check if we acknowledged their emotion
        if emotional_analysis.get('primary_emotion'):
            emotion = emotional_analysis['primary_emotion']
            if emotion in response_lower or any(trigger in response_lower for trigger in self.empathy_triggers.get(emotion, [])):
                empathy_score += 1
        
        return {
            'empathy_score': min(empathy_score / 5.0, 1.0),  # Normalize to 0-1
            'matched_phrases': matched_phrases,
            'acknowledged_emotion': emotional_analysis.get('primary_emotion') in response_lower if emotional_analysis.get('primary_emotion') else False
        }
    
    def _calculate_empathy_adjustment(self, emotional_analysis: Dict[str, Any], empathetic_response: Dict[str, Any]) -> float:
        """Calculate how much to adjust empathy level"""
        adjustment = 0.0
        
        # If user showed strong emotion but we didn't respond empathetically
        if emotional_analysis.get('overall_intensity', 0) > 0.5 and empathetic_response.get('empathy_score', 0) < 0.3:
            adjustment += 0.1  # Increase empathy
        
        # If user showed emotion and we responded well
        elif emotional_analysis.get('overall_intensity', 0) > 0.3 and empathetic_response.get('empathy_score', 0) > 0.7:
            adjustment += 0.05  # Reinforce empathy
        
        # If we over-empathized to neutral input
        elif emotional_analysis.get('overall_intensity', 0) < 0.2 and empathetic_response.get('empathy_score', 0) > 0.8:
            adjustment -= 0.03  # Slight reduction
        
        return adjustment
    
    def _apply_empathy_adjustment(self, adjustment: float, experience_data: Dict[str, Any], emotional_analysis: Dict[str, Any]) -> None:
        """Apply empathy adjustment with bounds checking"""
        old_level = self.current_level
        
        # Scale adjustment by adaptation rate
        scaled_adjustment = adjustment * self.adaptation_rate
        
        # Apply adjustment
        self.current_level += scaled_adjustment
        
        # Enforce bounds
        self.current_level = max(self.min_level, min(self.max_level, self.current_level))
        
        # Log significant changes
        if abs(old_level - self.current_level) > 0.03:
            self.logger.info(f"Empathy adjusted: {old_level:.3f} -> {self.current_level:.3f}")
        
        # Record emotional interaction
        self.emotional_interactions.append({
            'timestamp': experience_data.get('timestamp', datetime.now().isoformat()),
            'old_level': old_level,
            'new_level': self.current_level,
            'adjustment': scaled_adjustment,
            'emotional_intensity': emotional_analysis.get('overall_intensity', 0),
            'primary_emotion': emotional_analysis.get('primary_emotion'),
            'empathetic_response': scaled_adjustment > 0
        })
        
        # Maintain history size
        if len(self.emotional_interactions) > 100:
            self.emotional_interactions = self.emotional_interactions[-50:]
    
    def get_empathy_modifiers(self, emotional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get empathy-based response modifiers"""
        level = self.current_level
        
        base_modifiers = {
            'emotional_awareness': level,
            'response_warmth': level * 0.8,
            'validation_tendency': level * 0.9
        }
        
        if emotional_context and emotional_context.get('requires_empathy'):
            primary_emotion = emotional_context.get('primary_emotion')
            intensity = emotional_context.get('overall_intensity', 0)
            
            if primary_emotion == 'sadness':
                base_modifiers.update({
                    'tone': 'gentle_supportive',
                    'phrases': ['I\'m sorry you\'re going through this', 'That sounds really difficult', 'I can understand why you\'d feel that way'],
                    'avoid_phrases': ['cheer up', 'look on the bright side', 'it could be worse']
                })
            elif primary_emotion == 'anxiety':
                base_modifiers.update({
                    'tone': 'calm_reassuring',
                    'phrases': ['It\'s understandable to feel worried', 'Let\'s take this step by step', 'Your concerns are valid'],
                    'avoid_phrases': ['don\'t worry', 'calm down', 'it\'s no big deal']
                })
            elif primary_emotion == 'anger':
                base_modifiers.update({
                    'tone': 'understanding_validating',
                    'phrases': ['I can see why that would be frustrating', 'Your anger is understandable', 'That does sound unfair'],
                    'avoid_phrases': ['calm down', 'you\'re overreacting', 'it\'s not that bad']
                })
            elif primary_emotion == 'joy':
                base_modifiers.update({
                    'tone': 'enthusiastic_sharing',
                    'phrases': ['That\'s wonderful!', 'I\'m happy for you', 'How exciting!'],
                    'avoid_phrases': ['tone it down', 'be realistic']
                })
        
        return base_modifiers
    
    def should_show_empathy(self, context: Dict[str, Any]) -> bool:
        """Determine if situation calls for empathetic response"""
        if not context:
            return False
        
        user_input = context.get('parsed_input', {}).get('content', '')
        emotional_analysis = self.detect_emotional_state(user_input)
        
        return (emotional_analysis.get('requires_empathy', False) and 
                self.current_level > 0.4)
    
    def get_empathy_statistics(self) -> Dict[str, Any]:
        """Get empathy interaction statistics"""
        if not self.emotional_interactions:
            return {
                'total_emotional_interactions': 0,
                'empathy_success_rate': 0,
                'common_emotions': [],
                'average_emotional_intensity': 0
            }
        
        total_interactions = len(self.emotional_interactions)
        successful_empathy = sum(1 for interaction in self.emotional_interactions if interaction.get('empathetic_response', False))
        
        emotions = [interaction.get('primary_emotion') for interaction in self.emotional_interactions if interaction.get('primary_emotion')]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        common_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        intensities = [interaction.get('emotional_intensity', 0) for interaction in self.emotional_interactions]
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        return {
            'total_emotional_interactions': total_interactions,
            'empathy_success_rate': successful_empathy / total_interactions if total_interactions else 0,
            'common_emotions': [emotion[0] for emotion in common_emotions],
            'average_emotional_intensity': avg_intensity,
            'current_empathy_level': self.current_level
        }
