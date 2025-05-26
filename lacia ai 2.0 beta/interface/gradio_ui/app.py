#!/usr/bin/env python3
"""
Gradio Web Interface for Lacia AI
Interactive web-based chat interface with system monitoring
"""

try:
    import gradio as gr
    import json
    from datetime import datetime
    import time
    import threading
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    print("⚠️ Gradio not available. Web interface will not work.")

def create_gradio_interface(lacia_instance):
    """Create Gradio interface for Lacia AI"""
    
    if not GRADIO_AVAILABLE:
        raise ImportError("Gradio is required but not installed")
    
    # Global variables for interface state
    conversation_history = []
    
    def chat_with_lacia(message, history):
        """Process chat message and update history"""
        if not message.strip():
            return history, ""
        
        try:
            # Process message through Lacia AI
            response = lacia_instance.process_input(message)
            
            # Add to history
            history.append([message, response])
            
            # Store in conversation history
            conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': message,
                'lacia': response
            })
            
            return history, ""
            
        except Exception as e:
            error_response = f"❌ Error processing message: {str(e)}"
            history.append([message, error_response])
            return history, ""
    
    def get_system_status():
        """Get formatted system status"""
        try:
            status = lacia_instance.get_system_status()
            
            status_text = f"""
## 🤖 System Status

**Model Status:** {'✅ Loaded' if status['model_loaded'] else '❌ Not Loaded'}

### 😊 Emotional State
- **Current Mood:** {status['emotional_state'].get('current_mood', 'neutral')}
- **Energy Level:** {status['emotional_state'].get('energy_level', 0.5):.2f}
- **Stability:** {status['emotional_state'].get('stability', 0.5):.2f}

### 👤 Personality Traits
- **Assertiveness:** {status['personality_traits']['assertiveness']:.2f}
- **Empathy:** {status['personality_traits']['empathy']:.2f}
- **Curiosity:** {status['personality_traits']['curiosity']:.2f}

### 🧠 Memory Status
- **Short-term Memory:** {status['memory_status']['short_term_count']} items
- **Long-term Memory:** {status['memory_status']['long_term_count']} items

### 🔧 System Information
- **Skills Loaded:** {', '.join(status['skills_loaded'])}
- **Extensions:** {status['extensions_loaded']} loaded
- **Last Updated:** {datetime.now().strftime('%H:%M:%S')}
"""
            return status_text
            
        except Exception as e:
            return f"❌ Error getting system status: {str(e)}"
    
    def get_memory_info():
        """Get formatted memory information"""
        try:
            # Get recent memories
            recent_memories = lacia_instance.short_term_memory.get_recent_memories(10)
            ltm_count = lacia_instance.long_term_memory.get_memory_count()
            
            memory_text = f"""
## 🧠 Memory Information

### 📝 Recent Short-term Memories ({len(recent_memories)} shown)
"""
            
            for i, memory in enumerate(recent_memories, 1):
                content = memory.get('content', 'N/A')
                if len(content) > 100:
                    content = content[:97] + "..."
                
                memory_text += f"""
**{i}.** {content}
- Type: {memory.get('type', 'unknown')}
- Importance: {memory.get('importance', 0):.2f}
"""
            
            memory_text += f"\n- Total Interactions Stored: {ltm_count}\n"
            memory_text += """

### 💾 Long-term Memory
- This section shows how many important interactions Lacia has stored in permanent memory.
- These are remembered across sessions and can influence long-term behavior.
"""
            return memory_text
        
        except Exception as e:
            return f"\n❌ Error getting memory information: {str(e)}"

    with gr.Blocks(title="Lacia AI - Web Interface") as interface:
        gr.Markdown("# 🤖 Welcome to Lacia AI")
        gr.Markdown("Talk with your intelligent AI assistant!")
        
        chatbot = gr.Chatbot(label="Lacia AI Conversation")
        msg = gr.Textbox(placeholder="Type your message here and press Enter...")
        clear = gr.Button("🛉 Clear Chat")
        status_btn = gr.Button("📊 Show System Status")
        memory_btn = gr.Button("🧠 Show Memory Info")
        status_output = gr.Markdown()
        memory_output = gr.Markdown()

        def clear_chat():
            conversation_history.clear()
            return [], ""

        msg.submit(chat_with_lacia, [msg, chatbot], [chatbot, msg])
        clear.click(clear_chat, None, [chatbot, msg])
        status_btn.click(get_system_status, None, status_output)
        memory_btn.click(get_memory_info, None, memory_output)

    return interface
