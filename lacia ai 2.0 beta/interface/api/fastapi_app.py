#!/usr/bin/env python3
"""
FastAPI Application for Lacia AI
RESTful API interface with WebSocket support
"""

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    import json
    import asyncio
    from datetime import datetime
    from typing import Optional, Dict, List
except ImportError:
    # Graceful fallback if FastAPI is not installed
    print("⚠️ FastAPI not available. API interface will not work.")
    
    class BaseModel:
        pass
    
    def FastAPI(*args, **kwargs):
        return None

class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    timestamp: str
    emotion_state: Dict
    personality_traits: Dict
    processing_time: float

class SystemStatus(BaseModel):
    """System status model"""
    model_loaded: bool
    emotional_state: Dict
    personality_traits: Dict
    memory_status: Dict
    skills_loaded: List[str]
    extensions_loaded: int
    uptime: str

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

def create_api_app(lacia_instance):
    """Create FastAPI application with Lacia AI integration"""
    
    if FastAPI is None:
        raise ImportError("FastAPI is required but not installed")
    
    app = FastAPI(
        title="Lacia AI API",
        description="RESTful API for Lacia AI System",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # WebSocket connection manager
    manager = ConnectionManager()
    
    # Store startup time
    startup_time = datetime.now()
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """API documentation page"""
        return """
        <html>
            <head>
                <title>Lacia AI API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
                    .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .method { color: #007acc; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1 class="header">🤖 Lacia AI API</h1>
                <p>Welcome to the Lacia AI REST API interface!</p>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span> /chat
                    <p>Send a message to Lacia AI and get a response</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> /status
                    <p>Get current system status and information</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> /personality
                    <p>Get current personality traits</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> /emotion
                    <p>Get current emotional state</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> /memory
                    <p>Get memory status and recent memories</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">WebSocket</span> /ws
                    <p>Real-time chat via WebSocket connection</p>
                </div>
                
                <h2>API Documentation:</h2>
                <p><a href="/docs">Interactive API Documentation (Swagger UI)</a></p>
                <p><a href="/redoc">Alternative API Documentation (ReDoc)</a></p>
            </body>
        </html>
        """
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat(message: ChatMessage):
        """Process chat message through Lacia AI"""
        try:
            start_time = datetime.now()
            
            # Process message
            response = lacia_instance.process_input(message.message)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get current states
            emotion_state = lacia_instance.emotional_state.get_current_state()
            personality_traits = {
                'assertiveness': lacia_instance.assertiveness.get_current_level(),
                'empathy': lacia_instance.empathy.get_current_level(),
                'curiosity': lacia_instance.curiosity.get_current_level()
            }
            
            return ChatResponse(
                response=response,
                timestamp=datetime.now().isoformat(),
                emotion_state=emotion_state,
                personality_traits=personality_traits,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    
    @app.get("/status", response_model=SystemStatus)
    async def get_status():
        """Get system status"""
        try:
            status = lacia_instance.get_system_status()
            
            # Calculate uptime
            uptime = datetime.now() - startup_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            return SystemStatus(
                model_loaded=status['model_loaded'],
                emotional_state=status['emotional_state'],
                personality_traits=status['personality_traits'],
                memory_status=status['memory_status'],
                skills_loaded=status['skills_loaded'],
                extensions_loaded=status['extensions_loaded'],
                uptime=uptime_str
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")
    
    @app.get("/personality")
    async def get_personality():
        """Get current personality traits"""
        try:
            return {
                'assertiveness': lacia_instance.assertiveness.get_current_level(),
                'empathy': lacia_instance.empathy.get_current_level(),
                'curiosity': lacia_instance.curiosity.get_current_level(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Personality error: {str(e)}")
    
    @app.get("/emotion")
    async def get_emotion():
        """Get current emotional state"""
        try:
            emotion_state = lacia_instance.emotional_state.get_current_state()
            emotion_state['timestamp'] = datetime.now().isoformat()
            return emotion_state
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Emotion error: {str(e)}")
    
    @app.get("/memory")
    async def get_memory():
        """Get memory status"""
        try:
            # Get recent short-term memories
            recent_memories = lacia_instance.short_term_memory.get_recent_memories(10)
            
            # Get long-term memory count
            ltm_count = lacia_instance.long_term_memory.get_memory_count()
            
            return {
                'short_term_memory': {
                    'count': len(lacia_instance.short_term_memory.memories),
                    'recent_memories': [
                        {
                            'content': mem.get('content', '')[:100] + '...' if len(mem.get('content', '')) > 100 else mem.get('content', ''),
                            'type': mem.get('type', 'unknown'),
                            'importance': mem.get('importance', 0),
                            'timestamp': mem.get('timestamp', '')
                        }
                        for mem in recent_memories
                    ]
                },
                'long_term_memory': {
                    'count': ltm_count
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Memory error: {str(e)}")
    
    @app.get("/skills")
    async def get_skills():
        """Get available skills"""
        try:
            skills_info = {}
            for skill_name, skill in lacia_instance.skills.items():
                skills_info[skill_name] = {
                    'name': skill_name.replace('_', ' ').title(),
                    'description': getattr(skill, 'description', 'No description available'),
                    'available': True
                }
            
            return {
                'skills': skills_info,
                'count': len(lacia_instance.skills),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Skills error: {str(e)}")
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time chat"""
        await manager.connect(websocket)
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    # Parse message
                    message_data = json.loads(data)
                    user_message = message_data.get('message', '')
                    
                    if user_message:
                        # Process through Lacia AI
                        response = lacia_instance.process_input(user_message)
                        
                        # Get current states
                        emotion_state = lacia_instance.emotional_state.get_current_state()
                        personality_traits = {
                            'assertiveness': lacia_instance.assertiveness.get_current_level(),
                            'empathy': lacia_instance.empathy.get_current_level(),
                            'curiosity': lacia_instance.curiosity.get_current_level()
                        }
                        
                        # Send response
                        response_data = {
                            'type': 'chat_response',
                            'response': response,
                            'emotion_state': emotion_state,
                            'personality_traits': personality_traits,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        await manager.send_personal_message(
                            json.dumps(response_data), 
                            websocket
                        )
                    
                except json.JSONDecodeError:
                    # Handle plain text messages
                    response = lacia_instance.process_input(data)
                    await manager.send_personal_message(response, websocket)
                    
                except Exception as e:
                    error_response = {
                        'type': 'error',
                        'message': f'Processing error: {str(e)}',
                        'timestamp': datetime.now().isoformat()
                    }
                    await manager.send_personal_message(
                        json.dumps(error_response), 
                        websocket
                    )
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': str(datetime.now() - startup_time).split('.')[0]
        }
    
    return app

# For testing
if __name__ == "__main__":
    print("This module should be imported, not run directly")
    print("Use: python main.py --mode api")
