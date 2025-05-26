#!/usr/bin/env python3
"""
CLI Interface for Lacia AI
Provides interactive command-line interface with enhanced features
"""

import os
import sys
import json
import readline
import atexit
from datetime import datetime
from pathlib import Path

class CLIInterface:
    """Enhanced CLI Interface for Lacia AI"""
    
    def __init__(self, lacia_instance):
        self.lacia = lacia_instance
        self.history_file = "data/cli_history.txt"
        self.conversation_log = "data/conversation_log.json"
        self.running = True
        
        # Setup history
        self._setup_history()
        
        # Commands
        self.commands = {
            '/help': self.show_help,
            '/status': self.show_status,
            '/memory': self.show_memory,
            '/personality': self.show_personality,
            '/emotion': self.show_emotion,
            '/skills': self.show_skills,
            '/clear': self.clear_screen,
            '/save': self.save_conversation,
            '/load': self.load_conversation,
            '/history': self.show_history,
            '/quit': self.quit,
            '/exit': self.quit
        }
        
        self.conversation_history = []
    
    def _setup_history(self):
        """Setup readline history"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Load history if file exists
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
            
            # Set history length
            readline.set_history_length(1000)
            
            # Save history on exit
            atexit.register(self._save_history)
            
        except Exception as e:
            print(f"Warning: Could not setup history: {e}")
    
    def _save_history(self):
        """Save readline history"""
        try:
            readline.write_history_file(self.history_file)
        except Exception:
            pass
    
    def run(self):
        """Main CLI loop"""
        self._print_welcome()
        
        while self.running:
            try:
                # Get user input with prompt
                prompt = self._get_prompt()
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    # Process through Lacia AI
                    self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _print_welcome(self):
        """Print welcome message"""
        print("=" * 60)
        print("🤖 LACIA AI - Interactive CLI Interface")
        print("=" * 60)
        print("✨ Type your message and press Enter to chat")
        print("📋 Type /help for available commands")
        print("🚪 Type /quit or /exit to leave")
        print("=" * 60)
        print()
    
    def _get_prompt(self):
        """Get dynamic prompt based on system state"""
        # Get current emotional state
        emotion_state = self.lacia.emotional_state.get_current_state()
        current_mood = emotion_state.get('current_mood', 'neutral')
        
        # Mood emojis
        mood_emojis = {
            'joy': '😊',
            'sadness': '😔',
            'anger': '😠',
            'fear': '😨',
            'surprise': '😲',
            'disgust': '🤢',
            'neutral': '🤖'
        }
        
        mood_emoji = mood_emojis.get(current_mood, '🤖')
        
        return f"{mood_emoji} Owner> "
    
    def _handle_command(self, command):
        """Handle CLI commands"""
        cmd_parts = command.split()
        cmd = cmd_parts[0].lower()
        
        if cmd in self.commands:
            self.commands[cmd]()
        else:
            print(f"❌ Unknown command: {cmd}")
            print("📋 Type /help for available commands")
    
    def _process_user_input(self, user_input):
        """Process user input through Lacia AI"""
        print("🤔 Thinking...")
        
        try:
            # Process through Lacia AI
            response = self.lacia.process_input(user_input)
            
            # Display response
            print(f"\n💬 Lacia: {response}\n")
            
            # Save to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_input,
                'lacia': response
            })
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
    
    def show_help(self):
        """Show help information"""
        print("\n📋 AVAILABLE COMMANDS:")
        print("=" * 40)
        print("/help      - Show this help message")
        print("/status    - Show system status")
        print("/memory    - Show memory information")
        print("/personality - Show personality traits")
        print("/emotion   - Show emotional state")
        print("/skills    - Show available skills")
        print("/clear     - Clear screen")
        print("/save      - Save conversation")
        print("/load      - Load conversation")
        print("/history   - Show conversation history")
        print("/quit      - Exit the program")
        print("/exit      - Exit the program")
        print("=" * 40)
        print()
    
    def show_status(self):
        """Show system status"""
        print("\n📊 SYSTEM STATUS:")
        print("=" * 40)
        
        try:
            status = self.lacia.get_system_status()
            
            print(f"🤖 Model Loaded: {'✅' if status['model_loaded'] else '❌'}")
            print(f"🧠 Short-term Memory: {status['memory_status']['short_term_count']} items")
            print(f"💾 Long-term Memory: {status['memory_status']['long_term_count']} items")
            print(f"🔧 Skills: {', '.join(status['skills_loaded'])}")
            print(f"🔌 Extensions: {status['extensions_loaded']} loaded")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
        
        print("=" * 40)
        print()
    
    def show_memory(self):
        """Show memory information"""
        print("\n🧠 MEMORY STATUS:")
        print("=" * 40)
        
        try:
            # Short-term memory
            stm_memories = self.lacia.short_term_memory.get_recent_memories(5)
            print("📝 Recent Short-term Memories:")
            for i, memory in enumerate(stm_memories, 1):
                print(f"  {i}. {memory.get('content', 'N/A')[:50]}...")
            
            # Long-term memory count
            ltm_count = self.lacia.long_term_memory.get_memory_count()
            print(f"\n💾 Long-term Memory: {ltm_count} stored interactions")
            
        except Exception as e:
            print(f"❌ Error accessing memory: {e}")
        
        print("=" * 40)
        print()
    
    def show_personality(self):
        """Show personality traits"""
        print("\n👤 PERSONALITY TRAITS:")
        print("=" * 40)
        
        try:
            # Get current personality levels
            assertiveness = self.lacia.assertiveness.get_current_level()
            empathy = self.lacia.empathy.get_current_level()
            curiosity = self.lacia.curiosity.get_current_level()
            
            print(f"💪 Assertiveness: {assertiveness:.2f}")
            print(f"❤️ Empathy: {empathy:.2f}")
            print(f"🔍 Curiosity: {curiosity:.2f}")
            
        except Exception as e:
            print(f"❌ Error getting personality: {e}")
        
        print("=" * 40)
        print()
    
    def show_emotion(self):
        """Show emotional state"""
        print("\n😊 EMOTIONAL STATE:")
        print("=" * 40)
        
        try:
            emotion_state = self.lacia.emotional_state.get_current_state()
            
            print(f"🎭 Current Mood: {emotion_state.get('current_mood', 'neutral')}")
            print(f"⚡ Energy Level: {emotion_state.get('energy_level', 0.5):.2f}")
            print(f"😌 Stability: {emotion_state.get('stability', 0.5):.2f}")
            
            # Show emotion history if available
            if 'emotion_history' in emotion_state:
                recent_emotions = emotion_state['emotion_history'][-3:]
                print("📈 Recent Emotions:")
                for emotion in recent_emotions:
                    print(f"  • {emotion}")
            
        except Exception as e:
            print(f"❌ Error getting emotion state: {e}")
        
        print("=" * 40)
        print()
    
    def show_skills(self):
        """Show available skills"""
        print("\n🔧 AVAILABLE SKILLS:")
        print("=" * 40)
        
        try:
            for skill_name, skill in self.lacia.skills.items():
                print(f"⚙️ {skill_name.replace('_', ' ').title()}")
                
                # Try to get description if available
                if hasattr(skill, 'description'):
                    print(f"   └─ {skill.description}")
                elif hasattr(skill, '__doc__') and skill.__doc__:
                    print(f"   └─ {skill.__doc__.strip().split('.')[0]}")
                else:
                    print(f"   └─ Available")
        
        except Exception as e:
            print(f"❌ Error getting skills: {e}")
        
        print("=" * 40)
        print()
    
    def clear_screen(self):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self._print_welcome()
    
    def save_conversation(self):
        """Save conversation to file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Save conversation history
            with open(self.conversation_log, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            
            print(f"💾 Conversation saved to {self.conversation_log}")
            
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def load_conversation(self):
        """Load conversation from file"""
        try:
            if os.path.exists(self.conversation_log):
                with open(self.conversation_log, 'r') as f:
                    self.conversation_history = json.load(f)
                
                print(f"📂 Conversation loaded from {self.conversation_log}")
                print(f"📝 {len(self.conversation_history)} messages loaded")
            else:
                print("❌ No saved conversation found")
                
        except Exception as e:
            print(f"❌ Error loading conversation: {e}")
    
    def show_history(self):
        """Show conversation history"""
        print("\n📜 CONVERSATION HISTORY:")
        print("=" * 40)
        
        if not self.conversation_history:
            print("📝 No conversation history available")
        else:
            # Show last 5 exchanges
            recent_history = self.conversation_history[-5:]
            for i, exchange in enumerate(recent_history, 1):
                timestamp = exchange.get('timestamp', 'Unknown')
                user_msg = exchange.get('user', 'N/A')
                lacia_msg = exchange.get('lacia', 'N/A')
                
                print(f"\n{i}. [{timestamp[:19]}]")
                print(f"👤 User: {user_msg}")
                print(f"🤖 Owner: {lacia_msg[:100]}...")
        
        print("=" * 40)
        print()
    
    def quit(self):
        """Quit the CLI"""
        print("\n👋 Thank you for using Lacia AI!")
        
        # Save conversation before quitting
        if self.conversation_history:
            self.save_conversation()
        
        self.running = False

def create_cli_interface(lacia_instance):
    """Factory function to create CLI interface"""
    return CLIInterface(lacia_instance)

if __name__ == "__main__":
    # For testing purposes
    print("This module should be imported, not run directly")
