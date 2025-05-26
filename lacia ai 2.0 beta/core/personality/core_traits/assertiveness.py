"""
Assertiveness Trait Handler for Lacia AI
Manages assertiveness personality trait with dynamic adaptation
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

class AssertivenessHandler:
    """Handles assertiveness personality trait"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("personality", {}).get("assertiveness", {})
        self.base_level = self.config.get("base_level", 0.6)
        self.current_level = self.base_level
        self.adaptation_rate = self.config.get("adaptation_rate", 0.1)
        self.min_level = self.config.get("min_level", 0.1)
        self.max_level = self.config.get("max_level", 0.9)
        
        self.interaction_history = []
        self.adaptation_factors = {
            'positive_feedback': 0.05,
            'negative_feedback': -0.03,
            'conflict_resolution': 0.08,
            'passive_response': -0.02,
            'leadership_moment': 0.1
        }
        
        self.logger = logging.getLogger(__name__)
    
    def get_current_level(self) -> float:
        """Get current assertiveness level"""
        return self.current_level
    
    def update_from_interaction(self, experience_data: Dict[str, Any]) -> None:
        """Update assertiveness based on interaction experience"""
        try:
            user_input = experience_data.get('input', '').lower()
            ai_response = experience_data.get('response', '').lower()
            context = experience_data.get('context', {})
            
            # Analyze interaction patterns
            adjustment = 0.0
            
            # Check for assertiveness triggers in user input
            assertive_triggers = [
                'disagree', 'wrong', 'no', 'stop', 'enough',
                'demand', 'insist', 'require', 'must', 'need'
            ]
            
            passive_triggers = [
                'maybe', 'perhaps', 'sorry', 'excuse me',
                'if you don\'t mind', 'could you possibly'
            ]
            
            # User being assertive - we might need to match or moderate
            if any(trigger in user_input for trigger in assertive_triggers):
                # If user is being assertive, slightly increase our assertiveness
                adjustment += self.adaptation_factors['conflict_resolution'] * 0.5
            
            # User being passive - we might need to be more assertive
            elif any(trigger in user_input for trigger in passive_triggers):
                adjustment += self.adaptation_factors['leadership_moment'] * 0.3
            
            # Check our response patterns
            confident_phrases = [
                'i believe', 'i\'m certain', 'definitely', 'absolutely',
                'i recommend', 'you should', 'it\'s important'
            ]
            
            hesitant_phrases = [
                'i think maybe', 'perhaps', 'might be', 'could be',
                'i\'m not sure', 'possibly'
            ]
            
            if any(phrase in ai_response for phrase in confident_phrases):
                # We were assertive - small positive reinforcement
                adjustment += self.adaptation_factors['positive_feedback'] * 0.5
            elif any(phrase in ai_response for phrase in hesitant_phrases):
                # We were hesitant - might need more assertiveness
                adjustment += self.adaptation_factors['passive_response']
            
            # Apply adjustment
            if adjustment != 0:
                self._apply_adjustment(adjustment, experience_data)
                
        except Exception as e:
            self.logger.error(f"Error updating assertiveness: {e}")
    
    def _apply_adjustment(self, adjustment: float, experience_data: Dict[str, Any]) -> None:
        """Apply assertiveness adjustment with bounds checking"""
        old_level = self.current_level
        
        # Scale adjustment by adaptation rate
        scaled_adjustment = adjustment * self.adaptation_rate
        
        # Apply adjustment
        self.current_level += scaled_adjustment
        
        # Enforce bounds
        self.current_level = max(self.min_level, min(self.max_level, self.current_level))
        
        # Log significant changes
        if abs(old_level - self.current_level) > 0.05:
            self.logger.info(f"Assertiveness adjusted: {old_level:.3f} -> {self.current_level:.3f}")
        
        # Record interaction
        self.interaction_history.append({
            'timestamp': experience_data.get('timestamp', datetime.now().isoformat()),
            'old_level': old_level,
            'new_level': self.current_level,
            'adjustment': scaled_adjustment,
            'trigger': self._identify_trigger(experience_data)
        })
        
        # Maintain history size
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-50:]
    
    def _identify_trigger(self, experience_data: Dict[str, Any]) -> str:
        """Identify what triggered the assertiveness change"""
        user_input = experience_data.get('input', '').lower()
        
        if any(word in user_input for word in ['disagree', 'wrong', 'no']):
            return 'disagreement'
        elif any(word in user_input for word in ['demand', 'insist', 'must']):
            return 'user_assertive'
        elif any(word in user_input for word in ['maybe', 'perhaps', 'sorry']):
            return 'user_passive'
        else:
            return 'general_interaction'
    
    def get_assertiveness_modifier(self) -> Dict[str, Any]:
        """Get assertiveness-based response modifiers"""
        level = self.current_level
        
        if level >= 0.8:
            return {
                'tone': 'confident',
                'directness': 'high',
                'phrases': ['I strongly believe', 'It\'s clear that', 'Definitely'],
                'avoid_phrases': ['maybe', 'perhaps', 'might be']
            }
        elif level >= 0.6:
            return {
                'tone': 'balanced',
                'directness': 'medium',
                'phrases': ['I think', 'I believe', 'It seems'],
                'avoid_phrases': ['I\'m not sure']
            }
        elif level >= 0.4:
            return {
                'tone': 'gentle',
                'directness': 'medium',
                'phrases': ['I suggest', 'Consider that', 'It might be'],
                'avoid_phrases': ['absolutely', 'definitely']
            }
        else:
            return {
                'tone': 'tentative',
                'directness': 'low',
                'phrases': ['Perhaps', 'Maybe', 'It could be'],
                'avoid_phrases': ['I\'m certain', 'definitely']
            }
    
    def reset_to_base(self) -> None:
        """Reset assertiveness to base level"""
        self.current_level = self.base_level
        self.logger.info(f"Assertiveness reset to base level: {self.base_level}")
    
    def get_trend_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Analyze assertiveness trends over time"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_interactions = [
            interaction for interaction in self.interaction_history
            if datetime.fromisoformat(interaction['timestamp']) > cutoff_date
        ]
        
        if not recent_interactions:
            return {
                'trend': 'stable',
                'average_level': self.current_level,
                'change_frequency': 0,
                'dominant_triggers': []
            }
        
        levels = [interaction['new_level'] for interaction in recent_interactions]
        triggers = [interaction['trigger'] for interaction in recent_interactions]
        
        # Calculate trend
        if len(levels) > 1:
            trend_direction = levels[-1] - levels[0]
            if trend_direction > 0.1:
                trend = 'increasing'
            elif trend_direction < -0.1:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Find dominant triggers
        trigger_counts = {}
        for trigger in triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        dominant_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'trend': trend,
            'average_level': sum(levels) / len(levels),
            'change_frequency': len(recent_interactions),
            'dominant_triggers': [trigger[0] for trigger in dominant_triggers],
            'recent_range': (min(levels), max(levels))
        }
    
    def should_be_assertive(self, context: Dict[str, Any]) -> bool:
        """Determine if situation calls for assertiveness"""
        # Check context for assertiveness cues
        user_input = context.get('parsed_input', {}).get('content', '').lower()
        
        assertiveness_cues = [
            'help me decide', 'what should i do', 'give me advice',
            'recommend', 'suggest', 'opinion', 'think'
        ]
        
        return any(cue in user_input for cue in assertiveness_cues) and self.current_level > 0.5
