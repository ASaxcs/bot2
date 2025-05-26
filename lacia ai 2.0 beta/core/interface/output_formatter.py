#!/usr/bin/env python3
"""
Output Formatter - Core Interface Component
Formats AI responses based on context, personality, and emotional state
"""

import re
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

class OutputFormatter:
    """Handles formatting of AI responses with personality and emotional context"""
    
    def __init__(self, config: dict):
        self.config = config
        self.formatting_config = config.get("output_formatting", {})
        
        # Initialize formatting rules
        self.personality_modifiers = {
            'assertiveness': {
                'high': ['confidently', 'clearly', 'decisively'],
                'medium': ['thoughtfully', 'considerately'],
                'low': ['gently', 'tentatively', 'perhaps']
            },
            'empathy': {
                'high': ['I understand', 'I can imagine', 'That must be'],
                'medium': ['I see', 'I appreciate'],
                'low': ['Noted', 'Acknowledged']
            },
            'curiosity': {
                'high': ['That\'s fascinating!', 'I\'m intrigued by', 'Tell me more about'],
                'medium': ['Interesting', 'I wonder'],
                'low': ['I see', 'Understood']
            }
        }
        
        self.emotional_modifiers = {
            'joy': {
                'prefixes': ['I\'m excited to', 'I\'m happy to', 'It\'s wonderful that'],
                'suffixes': ['!', '! 😊', '! This is great!'],
                'intensifiers': ['absolutely', 'definitely', 'certainly']
            },
            'sadness': {
                'prefixes': ['I understand this might be difficult', 'I can see this is challenging'],
                'suffixes': ['.', '...', '. I\'m here to help.'],
                'tone_words': ['gently', 'carefully', 'thoughtfully']
            },
            'anger': {
                'prefixes': ['I can sense some frustration', 'This seems important to you'],
                'suffixes': ['.', '. Let\'s work through this.'],
                'tone_words': ['directly', 'clearly', 'straightforwardly']
            },
            'fear': {
                'prefixes': ['I want to be careful here', 'Let me approach this thoughtfully'],
                'suffixes': ['. I\'m here to help.', '. We can take this step by step.'],
                'reassurance': ['Don\'t worry', 'It\'s okay', 'We\'ll figure this out']
            },
            'surprise': {
                'prefixes': ['Oh!', 'That\'s unexpected!', 'Interesting!'],
                'suffixes': ['!', '! That\'s new to me.'],
                'expressions': ['Wow', 'Amazing', 'Fascinating']
            },
            'disgust': {
                'prefixes': ['I understand your concern', 'That\'s certainly problematic'],
                'suffixes': ['.', '. Let\'s address this.'],
                'tone_words': ['carefully', 'appropriately']
            },
            'neutral': {
                'prefixes': ['Let me help you with that', 'I can assist with'],
                'suffixes': ['.', '. How can I help further?'],
                'tone_words': ['clearly', 'helpfully']
            }
        }
    
    def format(self, response: str, context: Dict[str, Any]) -> str:
        """Main formatting method"""
        try:
            # Get context information
            personality = context.get('personality', {})
            emotion = context.get('emotion', {})
            memory = context.get('memory', {})
            parsed_input = context.get('parsed_input', {})
            
            # Apply personality-based formatting
            formatted_response = self._apply_personality_formatting(response, personality)
            
            # Apply emotional formatting
            formatted_response = self._apply_emotional_formatting(formatted_response, emotion)
            
            # Apply memory-based context
            formatted_response = self._apply_memory_context(formatted_response, memory)
            
            # Apply general formatting rules
            formatted_response = self._apply_general_formatting(formatted_response)
            
            # Add personality signature if configured
            if self.formatting_config.get("add_personality_signature", False):
                formatted_response = self._add_personality_signature(formatted_response, personality, emotion)
            
            
            # Apply concise formatting for better user experience
            formatted_response = self.make_response_concise(formatted_response, context)
            
            return formatted_response
            
        except Exception as e:
            print(f"Formatting error: {e}")
            return response  # Return original response if formatting fails
    
    def _apply_personality_formatting(self, response: str, personality: Dict[str, float]) -> str:
        """Apply personality-based formatting modifications"""
        if not personality:
            return response
        
        # Get dominant personality trait
        dominant_trait = max(personality.items(), key=lambda x: x[1])
        trait_name, trait_value = dominant_trait
        
        # Determine trait level
        if trait_value > 0.7:
            level = 'high'
        elif trait_value > 0.4:
            level = 'medium'
        else:
            level = 'low'
        
        # Apply trait-specific modifications
        if trait_name in self.personality_modifiers:
            modifiers = self.personality_modifiers[trait_name].get(level, [])
            if modifiers and random.random() < 0.3:  # 30% chance to add modifier
                modifier = random.choice(modifiers)
                
                # Add modifier to beginning of response
                if not response.startswith(modifier):
                    response = f"{modifier}, {response.lower()}"
        
        return response
    
    def _apply_emotional_formatting(self, response: str, emotion: Dict[str, Any]) -> str:
        """Apply emotion-based formatting modifications"""
        if not emotion:
            return response
        
        current_mood = emotion.get('current_mood', 'neutral')
        energy_level = emotion.get('energy_level', 0.5)
        
        if current_mood in self.emotional_modifiers:
            mood_config = self.emotional_modifiers[current_mood]
            
            # Add emotional prefix (20% chance)
            if random.random() < 0.2 and 'prefixes' in mood_config:
                prefix = random.choice(mood_config['prefixes'])
                response = f"{prefix}: {response.lower()}"
            
            # Modify response ending based on emotion
            if 'suffixes' in mood_config:
                # Remove existing punctuation
                response = response.rstrip('.!?')
                suffix = random.choice(mood_config['suffixes'])
                response += suffix
            
            # Add intensifiers for high energy
            if energy_level > 0.7 and 'intensifiers' in mood_config:
                intensifier = random.choice(mood_config['intensifiers'])
                response = response.replace('very', intensifier)
        
        return response
    
    def _apply_memory_context(self, response: str, memory: Dict[str, Any]) -> str:
        """Apply memory-based context to response"""
        if not memory:
            return response
        
        # Check for relevant memories
        relevant_memories = memory.get('relevant_memories', [])
        
        if relevant_memories and random.random() < 0.15:  # 15% chance to reference memory
            memory_ref = random.choice(relevant_memories)
            memory_text = memory_ref.get('content', '')
            
            if len(memory_text) > 10:  # Ensure memory has substantial content
                # Add memory reference
                response = f"Remembering our previous conversation about {memory_text[:30]}..., {response.lower()}"
        
        return response
    
    def _apply_general_formatting(self, response: str) -> str:
        """Apply general formatting rules"""
        # Ensure proper capitalization
        response = self._fix_capitalization(response)
        
        # Fix spacing issues
        response = self._fix_spacing(response)
        
        # Ensure proper punctuation
        response = self._fix_punctuation(response)
        
        # Apply text flow improvements
        response = self._improve_text_flow(response)
        
        return response
    
    def _fix_capitalization(self, text: str) -> str:
        """Fix capitalization issues"""
        if not text:
            return text
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Fix capitalization after sentence endings
        sentences = re.split(r'([.!?]\s+)', text)
        fixed_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and sentence:  # Actual sentence content
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            fixed_sentences.append(sentence)
        
        return ''.join(fixed_sentences)
    
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing issues"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        text = re.sub(r'([.!?])\s*', r'\1 ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """Ensure proper punctuation"""
        if not text:
            return text
        
        # Ensure text ends with proper punctuation
        if not text[-1] in '.!?':
            text += '.'
        
        # Fix double punctuation
        text = re.sub(r'[.!?]{2,}', '.', text)
        
        return text
    
    def _improve_text_flow(self, text: str) -> str:
        """Improve text flow and readability"""
        # Split into sentences
        sentences = re.split(r'([.!?]\s+)', text)
        improved_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and sentence:  # Actual sentence content
                # Remove redundant phrases
                sentence = self._remove_redundancy(sentence)
                
                # Improve sentence structure
                sentence = self._improve_sentence_structure(sentence)
                
            improved_sentences.append(sentence)
        
        return ''.join(improved_sentences)
    
    def _remove_redundancy(self, sentence: str) -> str:
        """Remove redundant phrases"""
        redundant_patterns = [
            r'\b(very very|really really|quite quite)\b',
            r'\b(I think that I think|I believe that I believe)\b',
            r'\b(basically basically|essentially essentially)\b'
        ]
        
        for pattern in redundant_patterns:
            sentence = re.sub(pattern, lambda m: m.group(1).split()[0], sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def _improve_sentence_structure(self, sentence: str) -> str:
        """Improve sentence structure"""
        # Fix common structural issues
        sentence = re.sub(r'\bthat that\b', 'that', sentence, flags=re.IGNORECASE)
        sentence = re.sub(r'\band and\b', 'and', sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def _add_personality_signature(self, response: str, personality: Dict[str, float], emotion: Dict[str, Any]) -> str:
        """Add personality signature to response"""
        signatures = []
        
        # Add personality-based signatures
        for trait, value in personality.items():
            if value > 0.8:
                if trait == 'assertiveness':
                    signatures.append("speaking confidently")
                elif trait == 'empathy':
                    signatures.append("with understanding")
                elif trait == 'curiosity':
                    signatures.append("eagerly exploring ideas")
        
        # Add emotional signature
        current_mood = emotion.get('current_mood', 'neutral')
        if current_mood != 'neutral':
            signatures.append(f"feeling {current_mood}")
        
        if signatures and self.formatting_config.get("show_signatures", False):
            signature_text = " (" + ", ".join(signatures) + ")"
            response += signature_text
        
        return response
    
    def format_system_message(self, message: str, message_type: str = "info") -> str:
        """Format system messages"""
        type_prefixes = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'debug': '🔧'
        }
        
        prefix = type_prefixes.get(message_type, 'ℹ️')
        return f"{prefix} {message}"
    
    def format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for display"""
        formatted_history = []
        
        for i, interaction in enumerate(history):
            timestamp = interaction.get('timestamp', 'Unknown time')
            user_input = interaction.get('user_input', '')
            ai_response = interaction.get('ai_response', '')
            
            formatted_history.append(f"[{timestamp}]")
            formatted_history.append(f"User: {user_input}")
            formatted_history.append(f"Lacia: {ai_response}")
            formatted_history.append("")  # Empty line for separation
        
        return "\n".join(formatted_history)
    
    def format_debug_info(self, context: Dict[str, Any]) -> str:
        """Format debug information"""
        debug_lines = ["🔧 Debug Information:"]
        
        # Personality info
        personality = context.get('personality', {})
        if personality:
            debug_lines.append("Personality Traits:")
            for trait, value in personality.items():
                debug_lines.append(f"  • {trait.title()}: {value:.2f}")
        
        # Emotional info
        emotion = context.get('emotion', {})
        if emotion:
            debug_lines.append("Emotional State:")
            debug_lines.append(f"  • Mood: {emotion.get('current_mood', 'neutral')}")
            debug_lines.append(f"  • Energy: {emotion.get('energy_level', 0.5):.2f}")
        
        # Memory info
        memory = context.get('memory', {})
        if memory:
            relevant_count = len(memory.get('relevant_memories', []))
            debug_lines.append(f"Memory Context: {relevant_count} relevant memories")
        
        return "\n".join(debug_lines)
    

    def make_response_concise(self, response: str, context: Dict[str, Any] = None) -> str:
        """Make response more concise and focused"""
        
        # Remove excessive personality trait mentions
        response = self.clean_personality_verbosity(response)
        
        # Check if this is a simple query that needs short response
        if context and self._is_simple_query(context):
            response = self.truncate_response(response, max_length=150)
        
        # Remove filler words and redundancy
        response = self.remove_filler_words(response)
        
        return response
    
    def clean_personality_verbosity(self, text: str) -> str:
        """Remove excessive personality trait mentions"""
        import re
        
        # Patterns to remove
        patterns = [
            r"with my \w+ level (of|at) \d+\.\d+",
            r"I'm feeling quite \w+ today, with a \w+ level of \d+\.\d+%?",
            r"Plus, with my energy level at \d+\.\d+",
            r"given my \w+ personality trait of \d+\.\d+",
            r"speaking from my \w+ level of \d+\.\d+"
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        # Clean up extra spaces and commas
        text = re.sub(r',\s*,', ',', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip(' ,.')
        
        return text
    
    def _is_simple_query(self, context: Dict[str, Any]) -> bool:
        """Determine if query is simple and needs short response"""
        parsed_input = context.get('parsed_input', {})
        
        # Check for simple task/scheduling requests
        if 'task' in str(context).lower() or 'schedule' in str(context).lower():
            return True
        
        # Check for short user input
        user_input = context.get('user_input', '')
        if len(user_input.split()) < 10:
            return True
        
        return False
    
    def truncate_response(self, response: str, max_length: int = 100) -> str:
        """Truncate response to maximum length while keeping it meaningful"""
        if len(response) <= max_length:
            return response
        
        # Find good truncation point (end of sentence)
        sentences = response.split('.')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + ".") <= max_length:
                truncated += sentence + "."
            else:
                break
        
        return truncated.strip() if truncated else response[:max_length].rsplit(' ', 1)[0] + "."
    
    def remove_filler_words(self, text: str) -> str:
        """Remove common filler words and phrases"""
        filler_patterns = [
            r"\b(um|uh|like|you know|sort of|kind of)\b",
            r"\b(basically|essentially|actually|literally)\b",
            r"\b(I think that|I believe that|it seems that)\b"
        ]
        
        for pattern in filler_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def get_formatting_stats(self) -> Dict[str, Any]:
        """Get formatting statistics"""
        return {
            "personality_modifiers_count": sum(len(modifiers) for trait_modifiers in self.personality_modifiers.values() 
                                             for modifiers in trait_modifiers.values()),
            "emotional_patterns_count": len(self.emotional_modifiers),
            "formatting_config": self.formatting_config
        }