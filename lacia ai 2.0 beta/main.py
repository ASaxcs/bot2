#!/usr/bin/env python3
"""
Lacia AI - Main Runner System (Modular Version)
A complex AI system with personality, memory, and emotional intelligence using your organized file structure
"""

import os
import sys
import logging
import asyncio
import argparse
import threading
import time
from pathlib import Path
from datetime import datetime
import warnings
from enum import Enum
import json
warnings.filterwarnings("ignore")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from your organized structure
try:
    # Fixed imports - config_manager is in root directory
    from config_manager import ConfigManager, load_config
    
    # Check if extension_manager exists in system directory
    try:
        from system.extension_manager import ExtensionManager
    except ImportError:
        print("⚠️ Extension manager not found, creating minimal version...")
        class ExtensionManager:
            def __init__(self):
                self.loaded_extensions = []
            def load_extensions(self):
                pass
    
    from core.cognition.processor import CognitionProcessor
    from core.cognition.decision import DecisionEngine
    from core.cognition.memory.short_term import ShortTermMemory
    from core.cognition.memory.long_term import LongTermMemory
    
    from core.personality.core_traits.assertiveness import AssertivenessHandler
    from core.personality.core_traits.empathy import EmpathyHandler
    from core.personality.core_traits.curiosity import CuriosityHandler
    from core.personality.adaptation.learning import PersonalityLearning
    from core.personality.adaptation.experience_handler import ExperienceHandler
    
    from core.personality.emotion.state_manager import EmotionalStateManager
    from core.personality.emotion.dialogue_triggers import DialogueTriggers
    from core.personality.emotion.event_triggers import EventEmotionTrigger
    
    from core.interface.input_parser import InputParser
    from core.interface.output_formatter import OutputFormatter
    
    from interface.cli.main import CLIInterface
    from interface.api.fastapi_app import create_api_app
    from interface.gradio_ui.app import create_gradio_interface
    
    from modules.skills.analog_hack import AnalogHackSkill
    from modules.skills.scheduling import Scheduler
    from modules.skills.translation import TranslationSkill
    
except ImportError as e:
    # Extract detailed error information
    error_name = getattr(e, 'name', str(e))
    error_path = getattr(e, 'path', ['unknown'])
    
    # Determine the file doing the import
    import traceback
    caller_trace = traceback.extract_tb(sys.exc_info()[2])
    importer_file = caller_trace[-1].filename if caller_trace else 'unknown'
    
    # Check if this is a circular import error
    is_circular = "cannot import name" in str(e) and "from partially initialized module" in str(e)
    
    # Check if module file actually exists
    module_parts = str(e).split("'")[1] if "'" in str(e) else error_name
    possible_locations = []
    
    if isinstance(module_parts, str):
        # Handle different import patterns
        if "." in module_parts:
            parts = module_parts.split(".")
            possible_locations = [
                os.path.join(os.getcwd(), *parts[:-1], f"{parts[-1]}.py"),
                os.path.join(os.getcwd(), *parts) + ".py",
                os.path.join(os.getcwd(), *parts, "__init__.py")
            ]
        else:
            possible_locations = [
                os.path.join(os.getcwd(), f"{module_parts}.py"),
                os.path.join(os.getcwd(), module_parts, "__init__.py")
            ]
    
    existing_files = []
    for loc in possible_locations:
        if os.path.exists(loc):
            existing_files.append(loc)

    # Format detailed error message
    error_msg = [
        f"\n❌❌❌ IMPORT ERROR DETECTED ❌❌❌",
        f"├─ Problematic module: {module_parts}",
        f"├─ Error type: {type(e).__name__}",
        f"├─ Error message: {str(e)}",
        f"├─ Import triggered by: {importer_file}",
        f"├─ Possible causes:",
        f"│  • File not found" if not existing_files else f"│  • Incorrect class/function name",
        f"│  • Circular import" if is_circular else "",
        f"│  • Invalid directory structure",
        f"└─ SOLUTION:"
    ]
    
    if existing_files:
        error_msg.extend([
            f"   ✅ File found at: {existing_files[0]}",
            f"   • Check if the imported class/function exists in that file",
            f"   • Verify spelling (case-sensitive)",
            f"   • Check __init__.py files in related directories"
        ])
    else:
        error_msg.extend([
            f"   ❌ File not found. Expected locations:",
            *[f"     • {loc}" for loc in possible_locations],
            f"   • Ensure directory structure matches import statements",
            f"   • Create required files or fix import paths"
        ])
    
    if is_circular:
        error_msg.extend([
            f"   ⚠️ Circular import detected!",
            f"   • Move imports inside functions/methods",
            f"   • Use lazy imports if needed",
            f"   • Reorganize module structure"
        ])
    
    error_msg.extend([
        "",
        "🔍 DEBUGGING INFORMATION:",
        f"  - Working Directory: {os.getcwd()}",
        f"  - Python Path (sys.path):",
        *[f"    • {path}" for path in sys.path[:5]],
        f"  - Directory contents: {', '.join(os.listdir())}",
    ])
    
    core_dir = os.path.join(os.getcwd(), 'core')
    if os.path.exists(core_dir):
        error_msg.extend([
            f"  - Core directory contents:",
            *[f"    • {item}" for item in os.listdir(core_dir) if not item.startswith('__')]
        ])
    
    # Show missing files that need to be created
    error_msg.extend([
        "",
        "📋 MISSING FILES TO CREATE:",
    ])
    
    for loc in possible_locations:
        if not os.path.exists(loc):
            error_msg.append(f"  ❌ {loc}")
    
    print('\n'.join(error_msg))
    sys.exit(1)


# GGUF Model Interface
try:
    from llama_cpp import Llama
except ImportError:
    print("❌ llama-cpp-python not installed. Install with: pip install llama-cpp-python")
    sys.exit(1)


def make_json_serializable(obj):
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, '__dict__'):
        # Handle custom objects by converting to dict
        try:
            return make_json_serializable(obj.__dict__)
        except:
            return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)


class MistralGGUFInterface:
    """GGUF Model Interface for Mistral 7B"""
    
    def __init__(self, config: dict):
        self.config = config
        self.model_config = config.get("model", {})
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load Mistral 7B GGUF model"""
        model_path = self.model_config.get("model_path", "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        
        print(f"🔄 Loading Mistral 7B GGUF model: {model_path}")
        
        # Create models directory if it doesn't exist
        model_dir = os.path.dirname(model_path)
        if model_dir:
            os.makedirs(model_dir, exist_ok=True)
        
        # Check if model file exists
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            print(f"Please download the model from: https://huggingface.co/{self.model_config.get('model_id', 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF')}")
            print(f"And place it at: {model_path}")
            self.model = None
            return
        
        try:
            self.model = Llama(
                model_path=model_path,
                n_ctx=self.model_config.get("n_ctx", 2048),
                n_batch=self.model_config.get("n_batch", 512),
                n_threads=self.model_config.get("n_threads"),
                verbose=self.model_config.get("verbose", False)
            )
            
            print("✅ GGUF Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading GGUF model: {e}")
            print("Using fallback response system...")
            self.model = None
    
    def generate_response(self, prompt: str, context: dict) -> str:
        """Generate response using Mistral 7B GGUF"""
        if self.model is None:
            return self._fallback_response(prompt, context)
        
        try:
            # Create system prompt with personality and emotion
            system_prompt = self._create_system_prompt(context)
            
            # Format prompt for Mistral Instruct
            full_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
            
            # Generate response
            response = self.model(
                full_prompt,
                max_tokens=self.model_config.get("max_tokens", 512),
                temperature=self.model_config.get("temperature", 0.7),
                top_p=self.model_config.get("top_p", 0.9),
                stop=["</s>", "[INST]", "[/INST]"],
                echo=False
            )
            
            # Extract generated text
            generated_text = response["choices"][0]["text"].strip()
            
            return generated_text
            
        except Exception as e:
            print(f"Generation error: {e}")
            return self._fallback_response(prompt, context)
    
    def _create_system_prompt(self, context: dict) -> str:
        """Create system prompt based on personality and emotion"""
        personality = context.get("personality", {})
        emotion = context.get("emotion", {})
        
        return f"""You are Lacia, an AI assistant with a dynamic personality and emotional intelligence.

Current State:
- Personality: {personality}
- Current Mood: {emotion.get('current_mood', 'neutral')}
- Energy Level: {emotion.get('energy_level', 0.5)}

Instructions:
- Respond naturally with your current personality traits
- Consider your emotional state when responding
- Be helpful, engaging, and maintain personality consistency
- Show emotional intelligence and empathy
- Keep responses concise and natural"""
    
    def _fallback_response(self, prompt: str, context: dict) -> str:
        """Fallback response when model is unavailable"""
        responses = [
            "I understand you're asking about that. Let me think about it...",
            "That's an interesting question. From my perspective...",
            "I appreciate you sharing that with me. Here's what I think...",
            "Thank you for your input. I'd like to respond by saying...",
        ]
        
        import random
        base_response = random.choice(responses)
        
        emotion = context.get("emotion", {})
        mood = emotion.get("current_mood", "neutral")
        
        if mood == "joy":
            base_response += " I'm feeling quite positive about this!"
        elif mood == "sadness":
            base_response += " I'm approaching this thoughtfully."
        
        return base_response


class LaciaAI:
    """Main Lacia AI System - Now using modular architecture"""
    
    def __init__(self, config_manager: ConfigManager):
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print("🚀 Memulai Inisialisasi Lacia AI (Arsitektur Modular)...")

        # Store configuration manager and get config
        self.config_manager = config_manager
        self.config = self.config_manager.get_config()
        
        # Initialize extension manager
        self.extension_manager = ExtensionManager()
        
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory(self.config)
        self.long_term_memory = LongTermMemory(self.config)
        
        # Initialize personality traits
        self.assertiveness = AssertivenessHandler(self.config)
        self.empathy = EmpathyHandler(self.config)
        self.curiosity = CuriosityHandler(self.config)
        
        # Initialize personality adaptation
        self.personality_learning = PersonalityLearning(self.config)
        self.experience_handler = ExperienceHandler(self.config)
        
        # Initialize emotional system
        self.emotional_state = EmotionalStateManager(self.config)
        self.dialogue_triggers = DialogueTriggers(self.config)
        self.event_triggers = EventEmotionTrigger(self.emotional_state, self.config)
        
        # Initialize cognition
        self.cognition_processor = CognitionProcessor(
            self.short_term_memory, 
            self.long_term_memory,
            self.config
        )
        self.decision_engine = DecisionEngine(self.config)
        
        # Initialize interface components
        self.input_parser = InputParser(self.config)
        self.output_formatter = OutputFormatter(self.config)
        
        # Initialize model interface
        self.model_interface = MistralGGUFInterface(self.config)
        
        # Initialize skills
        self.skills = {
            'analog_hack': AnalogHackSkill(self.config),
            'scheduling': Scheduler(self.config),
            'translation': TranslationSkill(self.config)
        }
        
        # Load extensions
        self.extension_manager.load_extensions()
        
        print("✅ Lacia AI System Initialized!")
        self._print_status()
    
    def _print_status(self):
        """Print system initialization status"""
        model_config = self.config.get("model", {})
        print(f"📝 Model: {model_config.get('model_id', 'Unknown')}")
        print(f"📁 Model File: {model_config.get('model_basename', 'Unknown')}")
        print(f"🧠 Memory Systems: Active")
        print(f"❤️ Emotional System: Active")
        print(f"👤 Personality Traits: Assertiveness, Empathy, Curiosity")
        print(f"🔧 Skills Loaded: {len(self.skills)}")
        print(f"🔌 Extensions: {len(self.extension_manager.loaded_extensions)}")

    def process_input(self, user_input: str) -> str:
        """Process user input through the entire AI system"""
        try:
            # Parse input
            parsed_input = self.input_parser.parse(user_input)
            
            # Store in short-term memory - FIXED
            try:
                self.short_term_memory.add_memory(
                    {"content": user_input, "type": "user_input"}, 
                    importance=0.6
                )
            except Exception as e:
                self.logger.error(f"STM storage error: {e}")
            
            # Process emotional triggers
            try:
                emotion_context = self.dialogue_triggers.process_triggers(user_input)
                self.emotional_state.update_state(emotion_context)
            except Exception as e:
                self.logger.error(f"Emotion processing error: {e}")
                emotion_context = {}
            
            # Process event triggers
            try:
                detected_events = self.event_triggers.process_user_interaction(
                    user_input=user_input,
                    context={'parsed_input': make_json_serializable(parsed_input)}
                )
            except Exception as e:
                self.logger.error(f"Event trigger error: {e}")
                detected_events = []
            
            # Get personality context
            try:
                personality_context = {
                    'assertiveness': self.assertiveness.get_current_level(),
                    'empathy': self.empathy.get_current_level(),
                    'curiosity': self.curiosity.get_current_level()
                }
            except Exception as e:
                self.logger.error(f"Personality context error: {e}")
                personality_context = {}
            
            # Get memory context - FIXED
            try:
                memory_context = self.cognition_processor.get_context_for_query(user_input)
            except Exception as e:
                self.logger.error(f"Memory context error: {e}")
                memory_context = {}
            
            # Prepare context for model - FIXED
            full_context = {
                'personality': personality_context,
                'emotion': self.emotional_state.get_current_state(),
                'memory': memory_context,
                'parsed_input': make_json_serializable(parsed_input),
                'detected_events': [make_json_serializable(e) for e in detected_events] if detected_events else []
            }
            
            # Check if any skills should handle this input
            response = None
            for skill_name, skill in self.skills.items():
                try:
                    if hasattr(skill, 'can_handle') and skill.can_handle(user_input):
                        skill_response = skill.process(user_input, full_context)
                        if skill_response:
                            response = skill_response
                            break
                except Exception as e:
                    self.logger.error(f"Skill {skill_name} error: {e}")
                    continue
            
            if not response:
                # Generate response using model
                response = self.model_interface.generate_response(user_input, full_context)
            
            # Format output
            try:
                formatted_response = self.output_formatter.format(response, full_context)
            except Exception as e:
                self.logger.error(f"Output formatting error: {e}")
                formatted_response = response
            
            # Store response in memory - FIXED
            try:
                self.short_term_memory.add_memory(
                    {"content": formatted_response, "type": "ai_response"}, 
                    importance=0.5
                )
            except Exception as e:
                self.logger.error(f"Response storage error: {e}")
            
            # Update long-term memory if important - FIXED
            try:
                if self._is_important_interaction(user_input, formatted_response):
                    self.long_term_memory.store_interaction(
                        user_input, 
                        formatted_response, 
                        make_json_serializable(full_context)
                    )
            except Exception as e:
                self.logger.error(f"LTM storage error: {e}")
            
            # Learn from interaction - FIXED
            try:
                experience_data = {
                    'input': user_input,
                    'response': formatted_response,
                    'context': make_json_serializable(full_context),
                    'timestamp': datetime.now().isoformat()
                }

                self.experience_handler.record_experience(experience_data)
                self.personality_learning.learn_from_interaction(experience_data)

                # Update personality traits
                self.assertiveness.update_from_interaction(experience_data)
                self.empathy.update_from_interaction(experience_data)
                self.curiosity.update_from_interaction(experience_data)

            except Exception as e:
                self.logger.error(f"Experience recording error: {e}")

            return formatted_response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
 
    def _is_important_interaction(self, user_input: str, response: str) -> bool:
        """Determine if interaction should be stored in long-term memory"""
        importance_keywords = [
            'remember', 'important', 'significant', 'crucial', 
            'personal', 'preference', 'like', 'dislike', 'favorite'
        ]
        
        combined_text = (user_input + " " + response).lower()
        return any(keyword in combined_text for keyword in importance_keywords)
    
    def run_cli(self):
        """Run CLI interface using modular CLI component"""
        cli_interface = CLIInterface(self)
        cli_interface.run()
    
    async def run_api(self):
        """Run FastAPI server using modular API component"""
        try:
            app = create_api_app(self)
            import uvicorn
            
            interface_config = self.config.get("interface", {})
            port = interface_config.get("api_port", 8000)
            
            config = uvicorn.Config(app, host="0.0.0.0", port=port)
            server = uvicorn.Server(config)
            await server.serve()
            
        except ImportError:
            print("❌ FastAPI not installed. Install with: pip install fastapi uvicorn")
        except Exception as e:
            print(f"❌ API server error: {e}")
    
    def run_gradio(self):
        """Run Gradio web interface using modular Gradio component"""
        try:
            interface = create_gradio_interface(self)
            interface_config = self.config.get("interface", {})
            port = interface_config.get("gradio_port", 7860)
            
            interface.launch(server_port=port, share=False)
            
        except ImportError:
            print("❌ Gradio not installed. Install with: pip install gradio")
        except Exception as e:
            print(f"❌ Gradio interface error: {e}")
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        return {
            "model_loaded": self.model_interface.model is not None,
            "emotional_state": self.emotional_state.get_current_state(),
            "personality_traits": {
                'assertiveness': self.assertiveness.get_current_level(),
                'empathy': self.empathy.get_current_level(),
                'curiosity': self.curiosity.get_current_level()
            },
            "memory_status": {
                "short_term_count": len(self.short_term_memory.memories),
                "long_term_count": self.long_term_memory.get_memory_count()
            },
            "skills_loaded": list(self.skills.keys()),
            "extensions_loaded": len(self.extension_manager.loaded_extensions),
            "event_trigger_stats": self.event_triggers.get_trigger_statistics()
        }


def main():
    """Main entry point with improved error handling"""
    parser = argparse.ArgumentParser(description="Lacia AI - Complex AI System (Modular)")
    parser.add_argument("--mode", choices=["cli", "api", "gradio", "all"], 
                       default="cli", help="Interface mode")
    parser.add_argument("--config", default="config.json", 
                       help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize ConfigManager with proper error handling
    try:
        print(f"📝 Loading configuration from: {args.config}")
        
        # Ensure config path is a string
        config_path = str(args.config)
        
        # Initialize ConfigManager
        config_manager = ConfigManager(config_path)
        
        # Verify config was loaded properly
        config = config_manager.get_config()
        if not config:
            raise ValueError("Failed to load configuration")
        
        print(f"✅ Configuration loaded successfully")
        
        # Initialize Lacia AI
        lacia = LaciaAI(config_manager)
        
    except Exception as e:
        print(f"❌ Failed to initialize Lacia AI: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Print stack trace for debugging
        import traceback
        traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("1. Check if config_manager.py exists and is properly formatted")
        print("2. Verify all required module files exist")
        print("3. Check file permissions")
        return
    
    try:
        if args.mode == "cli":
            lacia.run_cli()
        elif args.mode == "api":
            asyncio.run(lacia.run_api())
        elif args.mode == "gradio":
            lacia.run_gradio()
        elif args.mode == "all":
            # Run multiple interfaces
            print("🚀 Starting all interfaces...")
            
            # Start API in background
            api_thread = threading.Thread(target=lambda: asyncio.run(lacia.run_api()))
            api_thread.daemon = True
            api_thread.start()
            
            # Start Gradio in background
            gradio_thread = threading.Thread(target=lacia.run_gradio)
            gradio_thread.daemon = True
            gradio_thread.start()
            
            # Run CLI in foreground
            time.sleep(2)  # Give other interfaces time to start
            print("🖥️ CLI ready (other interfaces running in background)")
            lacia.run_cli()
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down Lacia AI...")
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check dependencies - FIXED VERSION
    print("🔍 Checking dependencies...")
    
    # Check for llama-cpp-python by trying to import llama_cpp
    try:
        import llama_cpp
        print("✅ llama-cpp-python is installed")
    except ImportError:
        print("❌ llama-cpp-python not installed.")
        print("Install with: pip install llama-cpp-python")
        print("For GPU support: pip install llama-cpp-python[cuda]")
        sys.exit(1)
    
    # Print setup instructions
    print("\n📋 LACIA AI - MODULAR SETUP")
    print("="*50)
    print("1. Ensure all module files are created in your directory structure")
    print("2. Download GGUF model: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
    print("3. Place model file in 'models/' folder")
    print("4. Run with: python main.py --mode [cli|api|gradio|all]")
    print("="*50)
    print()
    
    main()