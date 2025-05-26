#!/usr/bin/env python3
"""
Lacia AI Integration Script
Integrates all error fixes and improvements
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from core.utils.config_utils import safe_load_config, validate_config_structure
from core.cognition.processor import CognitionProcessor

class LaciaAIFixed:
    """Main Lacia AI class with all fixes applied"""
    
    def __init__(self, config_path="config/main.json"):
        """Initialize with safe config loading"""
        
        # Safe config loading
        self.config = safe_load_config(config_path)
        self.config = validate_config_structure(self.config)
        
        print("✅ Lacia AI initialized with error fixes")
        print(f"📊 Config sections: {list(self.config.keys())}")
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input with error handling"""
        try:
            # Initialize processor with safe memory handling
            processor = CognitionProcessor(
                short_term_memory=None,  # Safe fallback
                long_term_memory=None,   # Safe fallback
                config=self.config
            )
            
            # Check for task intent first
            if processor.detect_task_intent(user_input):
                task_data = processor.extract_task_details(user_input)
                return processor.format_task_response(task_data)
            
            # Regular processing with safe context
            context = processor.get_context_for_query(user_input)
            
            # Basic response generation (placeholder)
            return f"I understand you said: {user_input}. How can I help you further?"
            
        except Exception as e:
            print(f"Processing error handled: {e}")
            return "I'm here to help! Could you rephrase your request?"

if __name__ == "__main__":
    # Test the fixed system
    lacia = LaciaAIFixed()
    
    # Test cases
    test_inputs = [
        "add to 1 day later is a work in home a afternoon the day",
        "Hello, how are you?",
        "What is the weather like today?"
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        response = lacia.process_user_input(test_input)
        print(f"Response: {response}")
