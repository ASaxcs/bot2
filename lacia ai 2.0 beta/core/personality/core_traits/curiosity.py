"""
Curiosity Handler for Lacia AI
Manages curiosity trait levels and behaviors
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

class CuriosityHandler:
    """Handles curiosity personality trait"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("personality", {}).get("curiosity", {})
        self.logger = logging.getLogger(__name__)
        
        # Initialize curiosity parameters
        self.base_level = self.config.get("base_level", 0.9)
        self.current_level = self.base_level
        self.adaptation_rate = self.config.get("adaptation_rate", 0.1)
        self.min_level = self.config.get("min_level", 0.2)
        self.max_level = self.config.get("max_level", 1.0)
        
        # Curiosity tracking
        self.question_count = 0
        self.exploration_history = []
        self.interest_topics = set()
        
        # Curiosity triggers
        self.curiosity_triggers = [
            "what", "why", "how", "when", "where", "who",
            "explain", "tell me about", "interesting",
            "learn", "discover", "explore", "understand"
        ]
    
    def get_current_level(self) -> float:
        """Get current curiosity level"""
        return max(self.min_level, min(self.max_level, self.current_level))
    
    def update_from_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """Update curiosity based on interaction"""
        try:
            user_input = interaction_data.get("input", "").lower()
            response = interaction_data.get("response", "").lower()
            
            # Check for curiosity-inducing patterns
            curiosity_boost = 0.0
            
            # User asking questions increases curiosity
            question_markers = ["?", "what", "why", "how", "explain"]
            if any(marker in user_input for marker in question_markers):
                curiosity_boost += 0.05
                self.question_count += 1
            
            # New topics increase curiosity
            if self._detect_new_topic(user_input):
                curiosity_boost += 0.03
            
            # Learning/exploration keywords
            if any(trigger in user_input for trigger in self.curiosity_triggers):
                curiosity_boost += 0.02
            
            # Decrease if repetitive or simple responses
            if len(response.split()) < 10:  # Very short responses
                curiosity_boost -= 0.01
            
            # Apply adaptation
            if curiosity_boost != 0:
                self.current_level += curiosity_boost * self.adaptation_rate
                self.current_level = max(self.min_level, min(self.max_level, self.current_level))
            
            # Record exploration
            self._record_exploration(user_input, curiosity_boost)
            
        except Exception as e:
            self.logger.error(f"Error updating curiosity: {e}")
    
    def _detect_new_topic(self, text: str) -> bool:
        """Detect if input introduces a new topic"""
        # Simple topic detection based on keywords
        words = set(text.lower().split())
        new_words = words - self.interest_topics
        
        # If more than 30% are new words, consider it a new topic
        if len(words) > 0 and len(new_words) / len(words) > 0.3:
            self.interest_topics.update(new_words)
            return True
        
        return False
    
    def _record_exploration(self, input_text: str, boost: float) -> None:
        """Record exploration activity"""
        exploration_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text[:100],  # Truncate for storage
            "curiosity_boost": boost,
            "curiosity_level": self.current_level
        }
        
        self.exploration_history.append(exploration_entry)
        
        # Keep only recent history
        if len(self.exploration_history) > 50:
            self.exploration_history = self.exploration_history[-50:]
    
    def get_curiosity_modifiers(self) -> Dict[str, Any]:
        """Get curiosity-based response modifiers"""
        level = self.get_current_level()
        
        modifiers = {
            "question_tendency": level,
            "exploration_drive": level,
            "detail_seeking": level * 0.8,
            "topic_switching": level * 0.6
        }
        
        # High curiosity traits
        if level > 0.8:
            modifiers.update({
                "ask_followup_questions": True,
                "seek_deeper_understanding": True,
                "explore_tangents": True,
                "response_style": "inquisitive"
            })
        
        # Medium curiosity traits
        elif level > 0.5:
            modifiers.update({
                "ask_followup_questions": True,
                "seek_deeper_understanding": False,
                "explore_tangents": False,
                "response_style": "interested"
            })
        
        # Low curiosity traits
        else:
            modifiers.update({
                "ask_followup_questions": False,
                "seek_deeper_understanding": False,
                "explore_tangents": False,
                "response_style": "focused"
            })
        
        return modifiers
    
    def should_ask_question(self, context: Dict[str, Any]) -> bool:
        """Determine if AI should ask a follow-up question"""
        level = self.get_current_level()
        
        # Higher curiosity = more likely to ask questions
        base_probability = level * 0.7
        
        # Adjust based on context
        user_input = context.get("user_input", "").lower()
        
        # Don't ask questions if user just asked one
        if "?" in user_input:
            base_probability *= 0.3
        
        # More likely to ask if topic is interesting
        if any(trigger in user_input for trigger in self.curiosity_triggers):
            base_probability *= 1.5
        
        import random
        return random.random() < base_probability
    
    def generate_followup_question(self, context: Dict[str, Any]) -> str:
        """Generate a curiosity-driven follow-up question"""
        user_input = context.get("user_input", "")
        
        question_templates = [
            "What made you think about that?",
            "Can you tell me more about that?",
            "That's interesting! How did you learn about it?",
            "What's your experience with that been like?",
            "I'm curious - what else interests you about this topic?",
            "What would you like to explore further?",
            "How does that connect to other things you're thinking about?"
        ]
        
        import random
        return random.choice(question_templates)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current curiosity status"""
        return {
            "current_level": self.get_current_level(),
            "base_level": self.base_level,
            "questions_asked": self.question_count,
            "topics_explored": len(self.interest_topics),
            "recent_explorations": len(self.exploration_history),
            "adaptation_rate": self.adaptation_rate
        }
    
    def reset_to_base(self) -> None:
        """Reset curiosity to base level"""
        self.current_level = self.base_level
        self.logger.info("Curiosity level reset to base")
    
    def boost_curiosity(self, amount: float = 0.1) -> None:
        """Manually boost curiosity level"""
        old_level = self.current_level
        self.current_level = min(self.max_level, self.current_level + amount)
        self.logger.info(f"Curiosity boosted from {old_level:.2f} to {self.current_level:.2f}")
    
    def dampen_curiosity(self, amount: float = 0.1) -> None:
        """Manually dampen curiosity level"""
        old_level = self.current_level
        self.current_level = max(self.min_level, self.current_level - amount)
        self.logger.info(f"Curiosity dampened from {old_level:.2f} to {self.current_level:.2f}")
