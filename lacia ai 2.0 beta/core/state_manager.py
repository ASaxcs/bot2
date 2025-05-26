"""
Emotional State Manager for Lacia AI
Manages the AI's emotional state, transitions, and emotional memory
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math

class EmotionalStateManager:
    def __init__(self, config):
        self.config = config
        print("EmotionalStateManager initialized (basic version)")
    
    def update_state(self, emotion_context):
        return {"current_mood": "neutral", "intensity": 0.0}
    
    def get_current_state(self):
        return {"current_mood": "neutral", "intensity": 0.0}


class EmotionType(Enum):
    """Base emotion types"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    CURIOSITY = "curiosity"  # <-- Tambahkan ini
    EMPATHY = "empathy"      # <-- Juga dibutuhkan berdasarkan event_triggers.py
    EXCITEMENT = "excitement" # <-- Juga dibutuhkan
    CONFUSION = "confusion"   # <-- Juga dibutuhkan

@dataclass
class EmotionalState:
    """Represents a complete emotional state"""
    primary_emotion: str
    intensity: float
    secondary_emotions: Dict[str, float]
    energy_level: float
    stability: float
    timestamp: str
    context: Optional[Dict[str, Any]] = None

class EmotionalStateManager:
    """Manages the AI's emotional state and transitions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Emotional configuration
        self.emotion_config = config.get("emotion", {})
        self.decay_rate = self.emotion_config.get("decay_rate", 0.1)
        self.transition_speed = self.emotion_config.get("transition_speed", 0.3)
        self.stability_factor = self.emotion_config.get("stability_factor", 0.7)
        self.energy_recovery_rate = self.emotion_config.get("energy_recovery_rate", 0.05)
        
        # Initialize current state
        self.current_state = EmotionalState(
            primary_emotion="neutral",
            intensity=0.0,
            secondary_emotions={},
            energy_level=0.7,
            stability=1.0,
            timestamp=datetime.now().isoformat()
        )
        
        # Emotional history
        self.emotion_history: List[EmotionalState] = []
        self.max_history_length = self.emotion_config.get("max_history", 100)
        
        # Emotional thresholds
        self.emotion_thresholds = self.emotion_config.get("thresholds", {
            "joy": 0.6,
            "sadness": 0.5,
            "anger": 0.7,
            "fear": 0.6,
            "surprise": 0.4,
            "disgust": 0.6
        })
        
        # Emotion interaction matrix (how emotions affect each other)
        self._init_emotion_interactions()
        
        # Emotional memory patterns
        self.emotional_patterns = {}
        
        self.logger.info("Emotional State Manager initialized")
    
    def _init_emotion_interactions(self):
        """Initialize how emotions interact with each other"""
        self.emotion_interactions = {
            "joy": {
                "sadness": -0.8,  # Joy suppresses sadness
                "anger": -0.6,    # Joy reduces anger
                "fear": -0.7,     # Joy counters fear
                "surprise": 0.3,  # Joy can enhance positive surprise
                "disgust": -0.4   # Joy reduces disgust
            },
            "sadness": {
                "joy": -0.9,      # Sadness suppresses joy
                "anger": 0.4,     # Sadness can lead to anger
                "fear": 0.3,      # Sadness can increase fear
                "surprise": -0.2, # Sadness dampens surprise
                "disgust": 0.2    # Sadness can increase disgust
            },
            "anger": {
                "joy": -0.7,      # Anger suppresses joy
                "sadness": 0.3,   # Anger can lead to sadness
                "fear": -0.5,     # Anger can overcome fear
                "surprise": -0.3, # Anger reduces surprise sensitivity
                "disgust": 0.5    # Anger enhances disgust
            },
            "fear": {
                "joy": -0.8,      # Fear suppresses joy
                "sadness": 0.4,   # Fear can lead to sadness
                "anger": 0.2,     # Fear can trigger defensive anger
                "surprise": 0.6,  # Fear heightens surprise
                "disgust": 0.3    # Fear can increase disgust
            },
            "surprise": {
                "joy": 0.4,       # Surprise can enhance joy
                "sadness": 0.2,   # Surprise can lead to sadness
                "anger": 0.3,     # Surprise can trigger anger
                "fear": 0.5,      # Surprise can trigger fear
                "disgust": 0.1    # Surprise slightly increases disgust
            },
            "disgust": {
                "joy": -0.6,      # Disgust suppresses joy
                "sadness": 0.3,   # Disgust can lead to sadness
                "anger": 0.4,     # Disgust can trigger anger
                "fear": 0.2,      # Disgust can increase fear
                "surprise": -0.1  # Disgust slightly dampens surprise
            }
        }
    
    def update_state(self, emotion_context: Dict[str, Any]) -> EmotionalState:
        """Update emotional state based on new context"""
        try:
            # Extract emotion information
            dominant_emotion = emotion_context.get("dominant_emotion", "neutral")
            emotion_scores = emotion_context.get("emotion_scores", {})
            trigger_intensity = emotion_context.get("intensity", 0.0)
            
            
            # Calculate new emotional state
            new_state = self._calculate_new_state(
                dominant_emotion, 
                emotion_scores, 
                trigger_intensity,
                emotion_context
            )
            
            # Apply temporal decay to current state
            self._apply_temporal_decay()
            
            # Blend with current state
            blended_state = self._blend_emotional_states(self.current_state, new_state)
            
            # Apply stability constraints
            stable_state = self._apply_stability_constraints(blended_state)
            
            # Update current state
            previous_state = self.current_state
            self.current_state = stable_state
            
            # Record state change
            self._record_state_change(previous_state, stable_state, emotion_context)
            
            # Update emotional patterns
            self._update_emotional_patterns(emotion_context)
            
            self.logger.debug(f"Emotional state updated: {dominant_emotion} (intensity: {trigger_intensity:.2f})")
            
            return self.current_state
            
        except Exception as e:
            self.logger.error(f"State update error: {e}")
            return self.current_state
    
    def _calculate_new_state(self, dominant_emotion: str, emotion_scores: Dict[str, float], 
                           intensity: float, context: Dict[str, Any]) -> EmotionalState:
        """Calculate new emotional state from input"""
        
        # Handle neutral state
        if dominant_emotion == "neutral" or intensity < 0.1:
            return EmotionalState(
                primary_emotion="neutral",
                intensity=0.0,
                secondary_emotions={},
                energy_level=self.current_state.energy_level,
                stability=min(1.0, self.current_state.stability + 0.1),
                timestamp=datetime.now().isoformat(),
                context=context
            )
        
        # Calculate secondary emotions based on interactions
        secondary_emotions = {}
        if dominant_emotion in self.emotion_interactions:
            interactions = self.emotion_interactions[dominant_emotion]
            
            for emotion, interaction_strength in interactions.items():
                if emotion in emotion_scores:
                    # Calculate secondary emotion strength
                    base_strength = emotion_scores.get(emotion, 0.0)
                    interaction_effect = intensity * interaction_strength
                    secondary_strength = base_strength + interaction_effect
                    
                    if secondary_strength > 0.1:  # Only include significant secondary emotions
                        secondary_emotions[emotion] = max(0.0, min(1.0, secondary_strength))
        
        # Calculate energy impact
        energy_impact = self._calculate_energy_impact(dominant_emotion, intensity)
        new_energy = max(0.0, min(1.0, self.current_state.energy_level + energy_impact))
        
        # Calculate stability impact
        stability_impact = self._calculate_stability_impact(dominant_emotion, intensity)
        new_stability = max(0.0, min(1.0, self.current_state.stability + stability_impact))
        
        return EmotionalState(
            primary_emotion=dominant_emotion,
            intensity=intensity,
            secondary_emotions=secondary_emotions,
            energy_level=new_energy,
            stability=new_stability,
            timestamp=datetime.now().isoformat(),
            context=context
        )
    
    def _calculate_energy_impact(self, emotion: str, intensity: float) -> float:
        """Calculate how emotion affects energy level"""
        energy_effects = {
            "joy": 0.3,        # Joy increases energy
            "sadness": -0.4,   # Sadness decreases energy
            "anger": 0.2,      # Anger can increase energy short-term
            "fear": -0.2,      # Fear decreases energy
            "surprise": 0.1,   # Surprise slightly increases energy
            "disgust": -0.1    # Disgust slightly decreases energy
        }
        
        base_effect = energy_effects.get(emotion, 0.0)
        return base_effect * intensity * self.transition_speed
    
    def _calculate_stability_impact(self, emotion: str, intensity: float) -> float:
        """Calculate how emotion affects stability"""
        stability_effects = {
            "joy": 0.1,        # Joy increases stability
            "sadness": -0.2,   # Sadness decreases stability
            "anger": -0.3,     # Anger significantly decreases stability
            "fear": -0.25,     # Fear decreases stability
            "surprise": -0.15, # Surprise decreases stability
            "disgust": -0.1    # Disgust slightly decreases stability
        }
        
        base_effect = stability_effects.get(emotion, 0.0)
        return base_effect * intensity * self.transition_speed
    
    def _apply_temporal_decay(self):
        """Apply temporal decay to current emotional state"""
        time_diff = self._get_time_since_last_update()
        decay_factor = math.exp(-self.decay_rate * time_diff)
        
        # Decay intensity
        self.current_state.intensity *= decay_factor
        
        # Decay secondary emotions
        decayed_secondary = {}
        for emotion, strength in self.current_state.secondary_emotions.items():
            decayed_strength = strength * decay_factor
            if decayed_strength > 0.05:  # Keep only significant emotions
                decayed_secondary[emotion] = decayed_strength
        
        self.current_state.secondary_emotions = decayed_secondary
        
        # Recover energy gradually
        energy_recovery = self.energy_recovery_rate * time_diff
        self.current_state.energy_level = min(1.0, 
            self.current_state.energy_level + energy_recovery)
        
        # Recover stability gradually
        stability_recovery = self.energy_recovery_rate * 0.5 * time_diff
        self.current_state.stability = min(1.0, 
            self.current_state.stability + stability_recovery)
    
    def _get_time_since_last_update(self) -> float:
        """Get time in minutes since last state update"""
        try:
            last_time = datetime.fromisoformat(self.current_state.timestamp)
            current_time = datetime.now()
            diff = current_time - last_time
            return diff.total_seconds() / 60.0  # Return minutes
        except:
            return 1.0  # Default to 1 minute if parsing fails
    
    def _blend_emotional_states(self, current: EmotionalState, new: EmotionalState) -> EmotionalState:
        """Blend current and new emotional states"""
        blend_factor = self.transition_speed
        
        # Determine primary emotion
        if new.intensity > current.intensity * (1 + blend_factor):
            primary_emotion = new.primary_emotion
            primary_intensity = current.intensity + (new.intensity - current.intensity) * blend_factor
        else:
            primary_emotion = current.primary_emotion
            primary_intensity = current.intensity * (1 - self.decay_rate * 0.1)
        
        # Blend secondary emotions
        blended_secondary = {}
        all_emotions = set(current.secondary_emotions.keys()) | set(new.secondary_emotions.keys())
        
        for emotion in all_emotions:
            current_strength = current.secondary_emotions.get(emotion, 0.0)
            new_strength = new.secondary_emotions.get(emotion, 0.0)
            
            blended_strength = current_strength + (new_strength - current_strength) * blend_factor
            if blended_strength > 0.05:
                blended_secondary[emotion] = blended_strength
        
        # Blend other properties
        blended_energy = current.energy_level + (new.energy_level - current.energy_level) * blend_factor
        blended_stability = current.stability + (new.stability - current.stability) * blend_factor
        
        return EmotionalState(
            primary_emotion=primary_emotion,
            intensity=max(0.0, primary_intensity),
            secondary_emotions=blended_secondary,
            energy_level=max(0.0, min(1.0, blended_energy)),
            stability=max(0.0, min(1.0, blended_stability)),
            timestamp=datetime.now().isoformat(),
            context=new.context
        )
    
    def _apply_stability_constraints(self, state: EmotionalState) -> EmotionalState:
        """Apply stability constraints to prevent extreme emotional swings"""
        stability_factor = state.stability * self.stability_factor
        
        # Limit intensity based on stability
        max_intensity = 0.3 + (0.7 * stability_factor)
        constrained_intensity = min(state.intensity, max_intensity)
        
        # Limit secondary emotion strengths
        constrained_secondary = {}
        for emotion, strength in state.secondary_emotions.items():
            max_secondary = 0.2 + (0.5 * stability_factor)
            constrained_secondary[emotion] = min(strength, max_secondary)
        
        return EmotionalState(
            primary_emotion=state.primary_emotion,
            intensity=constrained_intensity,
            secondary_emotions=constrained_secondary,
            energy_level=state.energy_level,
            stability=state.stability,
            timestamp=state.timestamp,
            context=state.context
        )
    
    def _record_state_change(self, previous: EmotionalState, current: EmotionalState, context: Dict[str, Any]):
        """Record emotional state change in history"""
        # Add to history
        self.emotion_history.append(previous)
        
        # Maintain history size
        if len(self.emotion_history) > self.max_history_length:
            self.emotion_history.pop(0)
        
        # Log significant changes
        if previous.primary_emotion != current.primary_emotion:
            self.logger.info(f"Emotion changed: {previous.primary_emotion} -> {current.primary_emotion}")
        
        intensity_change = abs(current.intensity - previous.intensity)
        if intensity_change > 0.3:
            self.logger.info(f"Intensity changed significantly: {previous.intensity:.2f} -> {current.intensity:.2f}")
    
    def _update_emotional_patterns(self, context: Dict[str, Any]):
        """Update emotional patterns based on triggers"""
        # This could be used for learning emotional responses
        # For now, we'll store basic pattern information
        dominant_emotion = context.get("dominant_emotion", "neutral")
        
        if dominant_emotion not in self.emotional_patterns:
            self.emotional_patterns[dominant_emotion] = {
                "frequency": 0,
                "average_intensity": 0.0,
                "triggers": []
            }
        
        pattern = self.emotional_patterns[dominant_emotion]
        pattern["frequency"] += 1
        
        # Update average intensity
        current_intensity = context.get("intensity", 0.0)
        pattern["average_intensity"] = (
            (pattern["average_intensity"] * (pattern["frequency"] - 1) + current_intensity) / 
            pattern["frequency"]
        )
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current emotional state as dictionary"""
        return {
            "current_mood": self.current_state.primary_emotion,
            "intensity": self.current_state.intensity,
            "secondary_emotions": self.current_state.secondary_emotions,
            "energy_level": self.current_state.energy_level,
            "stability": self.current_state.stability,
            "timestamp": self.current_state.timestamp
        }
    
    def get_emotional_summary(self) -> Dict[str, Any]:
        """Get comprehensive emotional summary"""
        return {
            "current_state": self.get_current_state(),
            "recent_emotions": [
                {
                    "emotion": state.primary_emotion,
                    "intensity": state.intensity,
                    "timestamp": state.timestamp
                }
                for state in self.emotion_history[-5:]  # Last 5 states
            ],
            "emotional_patterns": self.emotional_patterns,
            "stability_trend": self._calculate_stability_trend(),
            "energy_trend": self._calculate_energy_trend()
        }
    
    def _calculate_stability_trend(self) -> str:
        """Calculate stability trend over recent history"""
        if len(self.emotion_history) < 3:
            return "stable"
        
        recent_stability = [state.stability for state in self.emotion_history[-3:]]
        recent_stability.append(self.current_state.stability)
        
        if recent_stability[-1] > recent_stability[0]:
            return "improving"
        elif recent_stability[-1] < recent_stability[0]:
            return "declining"
        else:
            return "stable"
    
    def _calculate_energy_trend(self) -> str:
        """Calculate energy trend over recent history"""
        if len(self.emotion_history) < 3:
            return "stable"
        
        recent_energy = [state.energy_level for state in self.emotion_history[-3:]]
        recent_energy.append(self.current_state.energy_level)
        
        if recent_energy[-1] > recent_energy[0]:
            return "increasing"
        elif recent_energy[-1] < recent_energy[0]:
            return "decreasing"
        else:
            return "stable"
    
    def set_emotional_baseline(self, emotion: str, intensity: float = 0.3):
        """Set a baseline emotional state"""
        try:
            self.current_state = EmotionalState(
                primary_emotion=emotion,
                intensity=intensity,
                secondary_emotions={},
                energy_level=0.7,
                stability=0.8,
                timestamp=datetime.now().isoformat()
            )
            
            self.logger.info(f"Emotional baseline set: {emotion} ({intensity})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting baseline: {e}")
            return False
    
    def reset_emotional_state(self):
        """Reset to neutral emotional state"""
        self.current_state = EmotionalState(
            primary_emotion="neutral",
            intensity=0.0,
            secondary_emotions={},
            energy_level=0.7,
            stability=1.0,
            timestamp=datetime.now().isoformat()
        )
        
        self.logger.info("Emotional state reset to neutral")
    
    def get_emotion_influence_on_response(self) -> Dict[str, Any]:
        """Get how current emotion should influence response generation"""
        current_emotion = self.current_state.primary_emotion
        intensity = self.current_state.intensity
        energy = self.current_state.energy_level
        
        influence = {
            "response_style": self._get_response_style(current_emotion, intensity),
            "word_choice": self._get_word_choice_bias(current_emotion),
            "response_length": self._get_response_length_preference(energy),
            "enthusiasm_level": self._get_enthusiasm_level(current_emotion, energy),
            "empathy_modifier": self._get_empathy_modifier(current_emotion),
            "curiosity_modifier": self._get_curiosity_modifier(current_emotion, energy)
        }
        
        return influence
    
    def _get_response_style(self, emotion: str, intensity: float) -> str:
        """Determine response style based on emotion"""
        if intensity < 0.2:
            return "neutral"
        
        style_map = {
            "joy": "enthusiastic" if intensity > 0.6 else "positive",
            "sadness": "gentle" if intensity > 0.6 else "subdued",
            "anger": "firm" if intensity > 0.6 else "assertive",
            "fear": "cautious" if intensity > 0.6 else "careful",
            "surprise": "animated" if intensity > 0.6 else "curious",
            "disgust": "direct" if intensity > 0.6 else "critical"
        }
        
        return style_map.get(emotion, "neutral")
    
    def _get_word_choice_bias(self, emotion: str) -> List[str]:
        """Get word choice bias based on emotion"""
        word_biases = {
            "joy": ["wonderful", "amazing", "excellent", "fantastic", "delightful"],
            "sadness": ["unfortunately", "sadly", "regrettably", "difficult", "challenging"],
            "anger": ["unacceptable", "frustrating", "concerning", "problematic", "serious"],
            "fear": ["careful", "cautious", "uncertain", "concerning", "worried"],
            "surprise": ["interesting", "unexpected", "remarkable", "fascinating", "unusual"],
            "disgust": ["problematic", "concerning", "inappropriate", "unacceptable", "wrong"]
        }
        
        return word_biases.get(emotion, [])
    
    def _get_response_length_preference(self, energy: float) -> str:
        """Determine preferred response length based on energy"""
        if energy > 0.7:
            return "detailed"
        elif energy > 0.4:
            return "moderate"
        else:
            return "concise"
    
    def _get_enthusiasm_level(self, emotion: str, energy: float) -> float:
        """Calculate enthusiasm level"""
        base_enthusiasm = {
            "joy": 0.8,
            "surprise": 0.6,
            "anger": 0.7,
            "sadness": 0.2,
            "fear": 0.3,
            "disgust": 0.4,
            "neutral": 0.5
        }
        
        base = base_enthusiasm.get(emotion, 0.5)
        return base * energy
    
    def _get_empathy_modifier(self, emotion: str) -> float:
        """Get empathy modifier based on current emotion"""
        empathy_modifiers = {
            "joy": 1.2,      # Joy increases empathy
            "sadness": 1.4,  # Sadness significantly increases empathy
            "anger": 0.7,    # Anger decreases empathy
            "fear": 1.1,     # Fear slightly increases empathy
            "surprise": 1.0, # Surprise doesn't affect empathy much
            "disgust": 0.8   # Disgust decreases empathy
        }
        
        return empathy_modifiers.get(emotion, 1.0)
    
    def _get_curiosity_modifier(self, emotion: str, energy: float) -> float:
        """Get curiosity modifier based on emotion and energy"""
        curiosity_base = {
            "joy": 1.3,      # Joy increases curiosity
            "surprise": 1.5, # Surprise significantly increases curiosity
            "anger": 0.6,    # Anger decreases curiosity
            "sadness": 0.8,  # Sadness decreases curiosity
            "fear": 0.7,     # Fear decreases curiosity
            "disgust": 0.5   # Disgust decreases curiosity
        }
        
        base = curiosity_base.get(emotion, 1.0)
        return base * (0.5 + 0.5 * energy)  # Energy also affects curiosity
