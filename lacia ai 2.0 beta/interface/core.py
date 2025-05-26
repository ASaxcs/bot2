"""
Core Interface Gateway for Lacia AI System
Acts as bridge between user interfaces and the core AI engine.
"""

import logging
from datetime import datetime

class LaciaCoreInterface:
    """Main interface core handler between front-end and Lacia AI system"""
    
    def __init__(self, lacia_instance):
        self.lacia = lacia_instance
        self.logger = logging.getLogger("LaciaCoreInterface")
        self.conversation_log = []

    def handle_input(self, user_input: str) -> dict:
        """Handle user input and return formatted response"""
        try:
            self.logger.info(f"Received input: {user_input}")
            if not user_input.strip():
                return self._format_response("Input kosong, silakan ketik sesuatu.", error=True)
            
            response = self.lacia.process_input(user_input)
            
            record = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'response': response
            }
            self.conversation_log.append(record)
            return self._format_response(response)
        
        except Exception as e:
            self.logger.error(f"Error during input handling: {e}")
            return self._format_response("Terjadi kesalahan saat memproses input.", error=True)
    
    def get_status(self) -> dict:
        """Return current system status"""
        try:
            status = self.lacia.get_system_status()
            status['timestamp'] = datetime.now().isoformat()
            return {'success': True, 'status': status}
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_last_conversations(self, count: int = 5) -> list:
        """Return last N user-AI conversations"""
        return self.conversation_log[-count:]

    def _format_response(self, response: str, error: bool = False) -> dict:
        """Format response dictionary"""
        return {
            'success': not error,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }

    def clear_log(self):
        """Clear stored conversation log"""
        self.conversation_log = []
        return {'success': True, 'message': 'Log berhasil dibersihkan'}


