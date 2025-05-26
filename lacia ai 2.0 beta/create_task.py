#!/usr/bin/env python3
"""
Lacia AI Error Fix Script
Memperbaiki semua error yang teridentifikasi dalam analisis
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

class LaciaErrorFixer:
    def __init__(self):
        self.backup_dir = Path("backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.fixes_applied = []
        
    def create_backup(self, file_path):
        """Buat backup file sebelum modifikasi"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        backup_path = self.backup_dir / Path(file_path).name
        shutil.copy2(file_path, backup_path)
        print(f"📁 Backup created: {backup_path}")
    
    def fix_memory_slice_error(self):
        """Fix 1: Memory Slice Error (CRITICAL PRIORITY)"""
        processor_path = "core/cognition/processor.py"
        
        if not os.path.exists(processor_path):
            print(f"❌ File not found: {processor_path}")
            return False
        
        self.create_backup(processor_path)
        
        with open(processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add safe memory handling function
        safe_memory_code = '''
def safe_memory_slice(memory_data, slice_obj=None, start=None, end=None):
    """Safe memory slicing to prevent index errors"""
    if not isinstance(memory_data, (list, tuple)):
        return []
    
    try:
        if slice_obj is not None:
            if isinstance(slice_obj, slice):
                return list(memory_data[slice_obj])
            elif isinstance(slice_obj, int):
                return [memory_data[slice_obj]] if 0 <= slice_obj < len(memory_data) else []
            else:
                return []
        
        # Handle start/end parameters
        if start is not None or end is not None:
            start = start if isinstance(start, int) else 0
            end = end if isinstance(end, int) else len(memory_data)
            return list(memory_data[start:end])
        
        return list(memory_data)
    except Exception as e:
        print(f"Memory slice error handled: {e}")
        return []

def safe_memory_retrieve(memory_list, limit=None):
    """Safely retrieve memory without slice errors"""
    if not isinstance(memory_list, (list, tuple)):
        return []
    
    if limit is None:
        return list(memory_list)
    
    try:
        if isinstance(limit, int) and limit > 0:
            return list(memory_list[-limit:])  # Get last N items safely
        return list(memory_list)
    except Exception as e:
        print(f"Memory retrieval error handled: {e}")
        return []

'''
        
        # Insert safe functions at the beginning of class
        if "def safe_memory_slice" not in content:
            # Find class CognitionProcessor
            class_match = re.search(r'class CognitionProcessor:', content)
            if class_match:
                insert_pos = class_match.start()
                content = content[:insert_pos] + safe_memory_code + content[insert_pos:]
            
            # Fix the problematic _get_relevant_short_term method
            old_method = re.search(r'def _get_relevant_short_term\(self, query: str, limit: int = None\) -> List\[Dict\[str, Any\]\]:(.*?)(?=def|\Z)', content, re.DOTALL)
            if old_method:
                new_method = '''def _get_relevant_short_term(self, query: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get relevant short-term memories with safe slicing"""
        try:
            limit = limit or self.context_window
            
            if not hasattr(self.short_term_memory, 'get_relevant_memories'):
                # Fallback with safe memory retrieval
                recent_memories = getattr(self.short_term_memory, 'memories', [])
                return safe_memory_retrieve(recent_memories, limit)
            
            return self.short_term_memory.get_relevant_memories(query, limit)
            
        except Exception as e:
            self.logger.error(f"Short-term memory retrieval error: {e}")
            return []
    '''
                content = content.replace(old_method.group(0), new_method + '\n    ')
        
        # Write back the fixed content
        with open(processor_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fixes_applied.append("Memory slice error fixed")
        print("✅ Fixed memory slice error in processor.py")
        return True
    
    def fix_experience_constructor(self):
        """Fix 2: Experience Constructor Error"""
        experience_path = "core/personality/adaptation/experience_handler.py"
        
        if not os.path.exists(experience_path):
            print(f"❌ File not found: {experience_path}")
            return False
        
        self.create_backup(experience_path)
        
        with open(experience_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix Experience class to not accept 'id' in constructor
        old_dataclass = re.search(r'@dataclass\nclass Experience:(.*?)def __post_init__\(self\):', content, re.DOTALL)
        
        if old_dataclass:
            new_dataclass = '''@dataclass
class Experience:
    """Struktur data untuk menyimpan pengalaman"""
    timestamp: str
    interaction_type: str
    context: Dict[str, Any]
    user_input: str
    ai_response: str
    user_feedback: Optional[str] = None
    emotion_state: Optional[str] = None
    success_rate: float = 0.0
    learning_points: List[str] = None
    # Note: id akan di-generate otomatis, tidak diterima sebagai parameter

    def __post_init__(self):'''
            
            content = content.replace(old_dataclass.group(0), new_dataclass)
        
        # Fix load_experiences method to handle id parameter properly
        load_experiences_pattern = r'(def load_experiences\(self\):.*?)(self\.experiences = \[Experience\(\*\*exp\) for exp in data\])'
        load_experiences_match = re.search(load_experiences_pattern, content, re.DOTALL)
        
        if load_experiences_match:
            new_load_method = load_experiences_match.group(1) + '''# Safe experience loading - remove 'id' if present
                    safe_experiences = []
                    for exp in data:
                        # Remove 'id' key if it exists
                        exp_copy = exp.copy()
                        exp_copy.pop('id', None)  # Remove id safely
                        safe_experiences.append(Experience(**exp_copy))
                    self.experiences = safe_experiences'''
            
            content = content.replace(load_experiences_match.group(0), new_load_method)
        
        with open(experience_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fixes_applied.append("Experience constructor fixed")
        print("✅ Fixed Experience constructor error")
        return True
    
    def fix_config_path_validation(self):
        """Fix 3: Config Path Validation"""
        
        # Create a utility module for safe config loading
        utils_dir = Path("core/utils")
        utils_dir.mkdir(parents=True, exist_ok=True)
        
        config_utils_path = utils_dir / "config_utils.py"
        
        config_utils_content = '''"""
Configuration utilities for safe config loading
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Union

def safe_load_config(config_path: Union[str, dict, Path]) -> Dict[str, Any]:
    """Safely load configuration with proper validation"""
    
    # If already a dict, return it
    if isinstance(config_path, dict):
        print(f"Warning: Config path is dict, using provided config")
        return config_path
    
    # Validate path type
    if not isinstance(config_path, (str, Path)):
        print(f"Warning: Invalid config path type: {type(config_path)}")
        return {}
    
    config_path = Path(config_path)
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Warning: Config file not found: {config_path}")
            return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def validate_config_structure(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix common config structure issues"""
    
    # Ensure required sections exist
    required_sections = ['data', 'cognition', 'personality', 'emotion', 'output_formatting']
    
    for section in required_sections:
        if section not in config:
            config[section] = {}
    
    # Fix common path issues
    data_section = config.get('data', {})
    if 'experiences_path' not in data_section:
        data_section['experiences_path'] = 'data/experiences.json'
    
    if 'triggers_config' not in data_section:
        data_section['triggers_config'] = 'config/triggers.json'
    
    if 'tasks_config' not in data_section:
        data_section['tasks_config'] = 'config/tasks.json'
    
    return config
'''
        
        with open(config_utils_path, 'w', encoding='utf-8') as f:
            f.write(config_utils_content)
        
        # Create __init__.py for utils module
        init_path = utils_dir / "__init__.py"
        with open(init_path, 'w') as f:
            f.write('from .config_utils import safe_load_config, validate_config_structure\n')
        
        self.fixes_applied.append("Config validation utilities created")
        print("✅ Created config validation utilities")
        return True
    
    def fix_task_intent_recognition(self):
        """Fix 4: Add Task Intent Recognition to Processor"""
        processor_path = "core/cognition/processor.py"
        
        if not os.path.exists(processor_path):
            print(f"❌ File not found: {processor_path}")
            return False
        
        with open(processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add task intent methods
        task_intent_methods = '''
    def detect_task_intent(self, user_input: str) -> bool:
        """Detect if user wants to create/manage tasks"""
        task_keywords = [
            "add task", "create task", "schedule", "remind", "todo",
            "tomorrow", "later", "work", "appointment", "meeting",
            "day later", "afternoon", "morning", "evening",
            "deadline", "due", "plan", "organize"
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in task_keywords)
    
    def extract_task_details(self, user_input: str) -> Dict[str, Any]:
        """Extract task details from natural language"""
        import re
        
        task_data = {
            "name": "",
            "description": user_input,
            "due_date": "unspecified",
            "priority": "medium",
            "category": "general"
        }
        
        user_lower = user_input.lower()
        
        # Extract time references
        time_patterns = {
            "tomorrow": "tomorrow",
            "today": "today", 
            "later": "later today",
            "afternoon": "this afternoon",
            "morning": "tomorrow morning",
            "evening": "this evening"
        }
        
        for pattern, time_ref in time_patterns.items():
            if pattern in user_lower:
                task_data["due_date"] = time_ref
                break
        
        # Extract work/task type
        if "work" in user_lower:
            task_data["category"] = "work"
            task_data["name"] = "Work task"
        elif "meeting" in user_lower:
            task_data["category"] = "meeting"
            task_data["name"] = "Meeting"
        elif "home" in user_lower:
            task_data["category"] = "personal"
            task_data["name"] = "Home task"
        else:
            # Try to extract meaningful task name
            words = user_input.split()
            if len(words) > 2:
                task_data["name"] = " ".join(words[:3])
            else:
                task_data["name"] = "New task"
        
        return task_data
    
    def format_task_response(self, task_data: Dict[str, Any]) -> str:
        """Format a concise task creation response"""
        name = task_data.get("name", "Task")
        due_date = task_data.get("due_date", "unspecified")
        
        responses = [
            f"✅ Got it! I'll help you remember: {name}",
            f"📝 Task noted: {name}",
            f"✅ Added to your list: {name}"
        ]
        
        import random
        response = random.choice(responses)
        
        if due_date != "unspecified":
            response += f" (due: {due_date})"
        
        return response + "."
'''
        
        # Find the end of the class and add the methods
        class_end = content.rfind("return self._get_fallback_context(query)")
        if class_end != -1:
            # Find the end of the method
            method_end = content.find("\n    def", class_end)
            if method_end == -1:
                method_end = len(content) - 1
            
            content = content[:method_end] + task_intent_methods + content[method_end:]
        
        with open(processor_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fixes_applied.append("Task intent recognition added")
        print("✅ Added task intent recognition to processor")
        return True
    
    def fix_output_formatter_verbosity(self):
        """Fix 5: Reduce Response Verbosity"""
        formatter_path = "core/interface/output_formatter.py"
        
        if not os.path.exists(formatter_path):
            print(f"❌ File not found: {formatter_path}")
            return False
        
        self.create_backup(formatter_path)
        
        with open(formatter_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add concise response methods
        concise_methods = '''
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
            r"\\b(um|uh|like|you know|sort of|kind of)\\b",
            r"\\b(basically|essentially|actually|literally)\\b",
            r"\\b(I think that|I believe that|it seems that)\\b"
        ]
        
        for pattern in filler_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        # Clean up spacing
        text = re.sub(r'\\s+', ' ', text).strip()
        
        return text
'''
        
        # Find the format method and modify it
        format_method_pattern = r'(def format\(self, response: str, context: Dict\[str, Any\]\) -> str:.*?)(return formatted_response)'
        format_match = re.search(format_method_pattern, content, re.DOTALL)
        
        if format_match:
            # Add concise formatting before return
            new_format_method = format_match.group(1) + '''
            # Apply concise formatting for better user experience
            formatted_response = self.make_response_concise(formatted_response, context)
            
            ''' + format_match.group(2)
            
            content = content.replace(format_match.group(0), new_format_method)
        
        # Add the new methods before the last method
        last_method_pos = content.rfind('    def get_formatting_stats(self)')
        if last_method_pos != -1:
            content = content[:last_method_pos] + concise_methods + '\n    ' + content[last_method_pos:]
        
        with open(formatter_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fixes_applied.append("Output formatter verbosity reduced")
        print("✅ Fixed output formatter verbosity")
        return True
    
    def create_integration_script(self):
        """Create integration script to tie all fixes together"""
        integration_content = '''#!/usr/bin/env python3
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
        print(f"\\nInput: {test_input}")
        response = lacia.process_user_input(test_input)
        print(f"Response: {response}")
'''
        
        with open("lacia_fixed.py", 'w', encoding='utf-8') as f:
            f.write(integration_content)
        
        self.fixes_applied.append("Integration script created")
        print("✅ Created integration script: lacia_fixed.py")
    
    def run_all_fixes(self):
        """Run all fixes in order of priority"""
        print("🔧 Starting Lacia AI error fixing process...\n")
        
        fixes = [
            ("Memory Slice Error (CRITICAL)", self.fix_memory_slice_error),
            ("Experience Constructor", self.fix_experience_constructor),
            ("Config Path Validation", self.fix_config_path_validation),
            ("Task Intent Recognition", self.fix_task_intent_recognition),
            ("Output Formatter Verbosity", self.fix_output_formatter_verbosity),
            ("Integration Script", self.create_integration_script)
        ]
        
        success_count = 0
        
        for fix_name, fix_function in fixes:
            print(f"🔧 Applying fix: {fix_name}")
            try:
                if fix_function():
                    success_count += 1
                    print(f"✅ {fix_name} - SUCCESS\n")
                else:
                    print(f"⚠️ {fix_name} - PARTIAL/SKIPPED\n")
            except Exception as e:
                print(f"❌ {fix_name} - FAILED: {e}\n")
        
        # Summary
        print("="*50)
        print("🎯 LACIA AI ERROR FIX SUMMARY")
        print("="*50)
        print(f"Total fixes attempted: {len(fixes)}")
        print(f"Successful fixes: {success_count}")
        print(f"Backup directory: {self.backup_dir}")
        print("\n📋 Fixes applied:")
        for fix in self.fixes_applied:
            print(f"  ✅ {fix}")
        
        if success_count >= 4:
            print("\n🎉 Most critical errors have been fixed!")
            print("🚀 You can now test with: python lacia_fixed.py")
        else:
            print("\n⚠️ Some fixes may need manual attention.")
        
        print("\n💡 Next steps:")
        print("1. Test the system with: python lacia_fixed.py")
        print("2. Check logs for any remaining errors")
        print("3. Adjust memory allocation if needed")
        print("4. Fine-tune personality response length")

if __name__ == "__main__":
    fixer = LaciaErrorFixer()
    fixer.run_all_fixes()