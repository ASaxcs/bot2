"""
Personality Learning System
Handles adaptive learning and personality evolution based on interactions
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

class PersonalityLearning:
    """Manages personality adaptation and learning from experiences"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Learning parameters
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.3
        self.memory_decay = 0.95
        
        # Learning history
        self.interaction_history = []
        self.adaptation_log = []
        self.personality_evolution = {
            'assertiveness': [],
            'empathy': [],
            'curiosity': []
        }
        
        # Current learning state
        self.learning_momentum = {
            'positive_interactions': 0,
            'negative_interactions': 0,
            'neutral_interactions': 0
        }
        
        self.pattern_recognition = {
            'successful_patterns': [],
            'failed_patterns': [],
            'context_associations': {}
        }
    
    def learn_from_interaction(self, experience_data: Dict[str, Any]) -> Dict[str, float]:
        """Learn and adapt personality from interaction experience"""
        try:
            # Extract interaction components
            user_input = experience_data.get('input', '')
            ai_response = experience_data.get('response', '')
            context = experience_data.get('context', {})
            timestamp = experience_data.get('timestamp', datetime.now().isoformat())
            
            # Analyze interaction sentiment and outcome
            interaction_analysis = self._analyze_interaction(user_input, ai_response, context)
            
            # Update learning momentum
            self._update_learning_momentum(interaction_analysis)
            
            # Determine personality adjustments
            personality_adjustments = self._calculate_personality_adjustments(interaction_analysis)
            
            # Apply learning patterns
            self._update_pattern_recognition(interaction_analysis, personality_adjustments)
            
            # Store interaction in history
            self.interaction_history.append({
                'experience': experience_data,
                'analysis': interaction_analysis,
                'adjustments': personality_adjustments,
                'timestamp': timestamp
            })
            
            # Maintain history size
            if len(self.interaction_history) > 100:
                self.interaction_history.pop(0)
            
            # Log adaptation
            if any(abs(adj) > 0.05 for adj in personality_adjustments.values()):
                self.adaptation_log.append({
                    'timestamp': timestamp,
                    'trigger': interaction_analysis.get('primary_trigger', 'unknown'),
                    'adjustments': personality_adjustments,
                    'confidence': interaction_analysis.get('confidence', 0.5)
                })
            
            return personality_adjustments
            
        except Exception as e:
            self.logger.error(f"Learning error: {e}")
            return {'assertiveness': 0.0, 'empathy': 0.0, 'curiosity': 0.0}
    
    def _analyze_interaction(self, user_input: str, ai_response: str, context: Dict) -> Dict[str, Any]:
        """Analyze interaction to determine learning signals"""
        analysis = {
            'sentiment': 'neutral',
            'complexity': 0.5,
            'engagement_level': 0.5,
            'success_indicators': [],
            'failure_indicators': [],
            'primary_trigger': 'general',
            'confidence': 0.5
        }
        
        try:
            # Sentiment analysis (simple keyword-based)
            positive_words = ['thank', 'great', 'good', 'excellent', 'helpful', 'amazing', 'love', 'perfect']
            negative_words = ['bad', 'wrong', 'terrible', 'hate', 'awful', 'useless', 'confused', 'frustrated']
            
            user_text = user_input.lower()
            ai_text = ai_response.lower()
            combined_text = user_text + ' ' + ai_text
            
            positive_count = sum(1 for word in positive_words if word in combined_text)
            negative_count = sum(1 for word in negative_words if word in combined_text)
            
            if positive_count > negative_count:
                analysis['sentiment'] = 'positive'
                analysis['success_indicators'].append('positive_language')
            elif negative_count > positive_count:
                analysis['sentiment'] = 'negative' 
                analysis['failure_indicators'].append('negative_language')
            
            # Complexity analysis
            avg_word_length = np.mean([len(word) for sent in [user_input, ai_response] for word in sent.split()])
            analysis['complexity'] = min(1.0, avg_word_length / 10.0)
            
            # Engagement analysis
            question_count = user_input.count('?') + ai_response.count('?')
            exclamation_count = user_input.count('!') + ai_response.count('!')
            analysis['engagement_level'] = min(1.0, (question_count + exclamation_count) / 5.0)
            
            # Determine primary trigger
            if any(word in user_text for word in ['help', 'assist', 'support']):
                analysis['primary_trigger'] = 'help_seeking'
            elif any(word in user_text for word in ['explain', 'how', 'why', 'what']):
                analysis['primary_trigger'] = 'information_seeking'
            elif any(word in user_text for word in ['create', 'make', 'build', 'design']):
                analysis['primary_trigger'] = 'creative_request'
            elif any(word in user_text for word in ['feel', 'emotion', 'sad', 'happy', 'angry']):
                analysis['primary_trigger'] = 'emotional_expression'
            
            # Calculate confidence based on signal strength
            signal_strength = abs(positive_count - negative_count) + question_count + exclamation_count
            analysis['confidence'] = min(1.0, signal_strength / 5.0)
            
        except Exception as e:
            self.logger.error(f"Interaction analysis error: {e}")
        
        return analysis
    
    def _update_learning_momentum(self, analysis: Dict[str, Any]):
        """Update learning momentum based on interaction analysis"""
        sentiment = analysis.get('sentiment', 'neutral')
        
        if sentiment == 'positive':
            self.learning_momentum['positive_interactions'] += 1
        elif sentiment == 'negative':
            self.learning_momentum['negative_interactions'] += 1
        else:
            self.learning_momentum['neutral_interactions'] += 1
        
        # Apply decay to older momentum
        for key in self.learning_momentum:
            self.learning_momentum[key] *= self.memory_decay
    
    def _calculate_personality_adjustments(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate personality trait adjustments based on interaction analysis"""
        adjustments = {
            'assertiveness': 0.0,
            'empathy': 0.0,
            'curiosity': 0.0
        }
        
        try:
            sentiment = analysis.get('sentiment', 'neutral')
            primary_trigger = analysis.get('primary_trigger', 'general')
            confidence = analysis.get('confidence', 0.5)
            engagement = analysis.get('engagement_level', 0.5)
            
            # Base adjustment magnitude
            base_adjustment = self.learning_rate * confidence
            
            # Assertiveness adjustments
            if primary_trigger == 'help_seeking' and sentiment == 'positive':
                adjustments['assertiveness'] += base_adjustment * 0.5
            elif sentiment == 'negative' and 'confusion' in analysis.get('failure_indicators', []):
                adjustments['assertiveness'] += base_adjustment * 0.3
            elif primary_trigger == 'creative_request':
                adjustments['assertiveness'] += base_adjustment * 0.2
            
            # Empathy adjustments
            if primary_trigger == 'emotional_expression':
                adjustments['empathy'] += base_adjustment * 0.7
            elif sentiment == 'negative':
                adjustments['empathy'] += base_adjustment * 0.4
            elif 'positive_language' in analysis.get('success_indicators', []):
                adjustments['empathy'] += base_adjustment * 0.2
            
            # Curiosity adjustments
            if primary_trigger == 'information_seeking':
                adjustments['curiosity'] += base_adjustment * 0.6
            elif engagement > 0.7:
                adjustments['curiosity'] += base_adjustment * 0.3
            elif primary_trigger == 'creative_request':
                adjustments['curiosity'] += base_adjustment * 0.4
            
            # Apply momentum influence
            positive_momentum = self.learning_momentum['positive_interactions']
            negative_momentum = self.learning_momentum['negative_interactions']
            
            momentum_factor = (positive_momentum - negative_momentum) / 10.0
            momentum_factor = max(-0.5, min(0.5, momentum_factor))
            
            for trait in adjustments:
                adjustments[trait] += momentum_factor * base_adjustment * 0.2
            
            # Ensure adjustments are within reasonable bounds
            for trait in adjustments:
                adjustments[trait] = max(-0.1, min(0.1, adjustments[trait]))
                
        except Exception as e:
            self.logger.error(f"Adjustment calculation error: {e}")
        
        return adjustments
    
    def _update_pattern_recognition(self, analysis: Dict[str, Any], adjustments: Dict[str, float]):
        """Update pattern recognition based on successful/failed interactions"""
        try:
            pattern_key = f"{analysis.get('primary_trigger', 'general')}_{analysis.get('sentiment', 'neutral')}"
            
            # Determine if this was a successful pattern
            if analysis.get('sentiment') == 'positive' and any(abs(adj) > 0.02 for adj in adjustments.values()):
                if pattern_key not in [p['pattern'] for p in self.pattern_recognition['successful_patterns']]:
                    self.pattern_recognition['successful_patterns'].append({
                        'pattern': pattern_key,
                        'adjustments': adjustments.copy(),
                        'confidence': analysis.get('confidence', 0.5),
                        'count': 1,
                        'last_seen': datetime.now().isoformat()
                    })
                else:
                    # Update existing pattern
                    for pattern in self.pattern_recognition['successful_patterns']:
                        if pattern['pattern'] == pattern_key:
                            pattern['count'] += 1
                            pattern['last_seen'] = datetime.now().isoformat()
                            # Blend adjustments
                            for trait in adjustments:
                                pattern['adjustments'][trait] = (
                                    pattern['adjustments'][trait] * 0.8 + adjustments[trait] * 0.2
                                )
                            break
            
            # Store context associations
            context_key = analysis.get('primary_trigger', 'general')
            if context_key not in self.pattern_recognition['context_associations']:
                self.pattern_recognition['context_associations'][context_key] = {
                    'successful_traits': {'assertiveness': 0, 'empathy': 0, 'curiosity': 0},
                    'interaction_count': 0
                }
            
            context_data = self.pattern_recognition['context_associations'][context_key]
            context_data['interaction_count'] += 1
            
            if analysis.get('sentiment') == 'positive':
                for trait, adjustment in adjustments.items():
                    if adjustment > 0:
                        context_data['successful_traits'][trait] += 1
            
        except Exception as e:
            self.logger.error(f"Pattern recognition update error: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learning patterns and personality evolution"""
        return {
            'total_interactions': len(self.interaction_history),
            'learning_momentum': self.learning_momentum.copy(),
            'successful_patterns': len(self.pattern_recognition['successful_patterns']),
            'adaptation_frequency': len(self.adaptation_log),
            'recent_adaptations': self.adaptation_log[-5:] if self.adaptation_log else [],
            'context_associations': self.pattern_recognition['context_associations'].copy(),
            'personality_evolution_summary': {
                trait: {
                    'total_changes': len(changes),
                    'recent_trend': np.mean(changes[-10:]) if changes else 0.0
                }
                for trait, changes in self.personality_evolution.items()
            }
        }
    
    def predict_optimal_response_style(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Predict optimal personality configuration for given context"""
        try:
            primary_trigger = context.get('primary_trigger', 'general')
            
            # Check if we have learned patterns for this context
            if primary_trigger in self.pattern_recognition['context_associations']:
                context_data = self.pattern_recognition['context_associations'][primary_trigger]
                successful_traits = context_data['successful_traits']
                total_interactions = context_data['interaction_count']
                
                if total_interactions > 0:
                    return {
                        trait: min(1.0, score / total_interactions)
                        for trait, score in successful_traits.items()
                    }
            
            # Fallback to general successful patterns
            general_recommendations = {'assertiveness': 0.5, 'empathy': 0.5, 'curiosity': 0.5}
            
            for pattern in self.pattern_recognition['successful_patterns']:
                if pattern['count'] > 2:  # Only consider well-established patterns
                    for trait, adjustment in pattern['adjustments'].items():
                        general_recommendations[trait] += adjustment * 0.1
            
            # Normalize recommendations
            for trait in general_recommendations:
                general_recommendations[trait] = max(0.1, min(0.9, general_recommendations[trait]))
            
            return general_recommendations
            
        except Exception as e:
            self.logger.error(f"Response style prediction error: {e}")
            return {'assertiveness': 0.5, 'empathy': 0.5, 'curiosity': 0.5}
    
    def reset_learning_data(self):
        """Reset learning data (useful for testing or fresh starts)"""
        self.interaction_history.clear()
        self.adaptation_log.clear()
        self.learning_momentum = {
            'positive_interactions': 0,
            'negative_interactions': 0,
            'neutral_interactions': 0
        }
        self.pattern_recognition = {
            'successful_patterns': [],
            'failed_patterns': [],
            'context_associations': {}
        }
        
        for trait in self.personality_evolution:
            self.personality_evolution[trait].clear()
        
        self.logger.info("Learning data reset successfully")
    
    def save_learning_state(self, filepath: str) -> bool:
        """Save learning state to file"""
        try:
            learning_state = {
                'learning_momentum': self.learning_momentum,
                'pattern_recognition': self.pattern_recognition,
                'adaptation_log': self.adaptation_log[-50:],  # Save recent adaptations
                'personality_evolution': self.personality_evolution,
                'config': self.config,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(learning_state, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save learning state: {e}")
            return False
    
    def load_learning_state(self, filepath: str) -> bool:
        """Load learning state from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                learning_state = json.load(f)
            
            self.learning_momentum = learning_state.get('learning_momentum', self.learning_momentum)
            self.pattern_recognition = learning_state.get('pattern_recognition', self.pattern_recognition)
            self.adaptation_log = learning_state.get('adaptation_log', [])
            self.personality_evolution = learning_state.get('personality_evolution', self.personality_evolution)
            
            self.logger.info(f"Learning state loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load learning state: {e}")
            return False
