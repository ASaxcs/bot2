"""
Pydantic Schemas untuk Lacia AI FastAPI Application
Definisi model data untuk request dan response
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
import uuid

class BaseSchema(BaseModel):
    """Base schema dengan konfigurasi umum"""
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="forbid"
    )

# Enums untuk status dan tipe
class ExtensionType(str, Enum):
    """Tipe ekstensi"""
    CORE = "core"
    PLUGIN = "plugin"
    INTEGRATION = "integration"
    UTILITY = "utility"
    AI_MODEL = "ai_model"
    DATA_SOURCE = "data_source"
    OUTPUT_FORMAT = "output_format"

class ExtensionStatus(str, Enum):
    """Status ekstensi"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    LOADING = "loading"
    ERROR = "error"
    DISABLED = "disabled"

class MessageType(str, Enum):
    """Tipe pesan"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"

class SessionStatus(str, Enum):
    """Status session"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"

# Chat related schemas
class ChatMessage(BaseSchema):
    """Model untuk single chat message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.USER
    content: str = Field(..., min_length=1, max_length=32000)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

class ChatContext(BaseSchema):
    """Context untuk chat request"""
    conversation_history: Optional[List[ChatMessage]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    session_variables: Optional[Dict[str, Any]] = None
    active_extensions: Optional[List[str]] = None
    model_parameters: Optional[Dict[str, Any]] = None

class ChatRequest(BaseSchema):
    """Request untuk chat endpoint"""
    message: str = Field(..., min_length=1, max_length=32000, description="Pesan dari user")
    session_id: Optional[str] = Field(None, description="ID session untuk context")
    model: Optional[str] = Field("default", description="Model AI yang akan digunakan")
    context: Optional[ChatContext] = Field(None, description="Context tambahan untuk request")
    stream: bool = Field(False, description="Enable streaming response")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature untuk AI response")
    max_tokens: Optional[int] = Field(None, ge=1, le=8000, description="Maximum tokens untuk response")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if v and len(v) > 100:
            raise ValueError('Session ID too long')
        return v

class ChatResponse(BaseSchema):
    """Response dari chat endpoint"""
    response_id: str = Field(..., description="Unique ID untuk response")
    session_id: Optional[str] = Field(None, description="Session ID yang digunakan")
    message: str = Field(..., description="Response dari AI")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata tambahan")
    tokens_used: Optional[int] = Field(None, description="Jumlah tokens yang digunakan")
    processing_time: Optional[float] = Field(None, description="Waktu processing dalam detik")
    model_used: Optional[str] = Field(None, description="Model yang digunakan")
    extensions_used: Optional[List[str]] = Field(None, description="Ekstensi yang digunakan")

class StreamChunk(BaseSchema):
    """Chunk untuk streaming response"""
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    content: str = Field(..., description="Content chunk")
    index: int = Field(..., description="Index chunk dalam stream")
    is_final: bool = Field(False, description="Apakah ini chunk terakhir")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

# Session related schemas
class SessionMetadata(BaseSchema):
    """Metadata untuk session"""
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    client_info: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    custom_data: Optional[Dict[str, Any]] = None

class SessionRequest(BaseSchema):
    """Request untuk membuat session baru"""
    name: Optional[str] = Field(None, max_length=200, description="Nama session")
    description: Optional[str] = Field(None, max_length=1000, description="Deskripsi session")
    metadata: Optional[SessionMetadata] = Field(None, description="Metadata session")
    expires_in: Optional[int] = Field(None, ge=1, description="Session expires dalam detik")
    auto_cleanup: bool = Field(True, description="Auto cleanup ketika expired")

class SessionResponse(BaseSchema):
    """Response untuk session operations"""
    session_id: str = Field(..., description="Unique session ID")
    name: Optional[str] = None
    description: Optional[str] = None
    status: SessionStatus = Field(SessionStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[SessionMetadata] = None
    message_count: Optional[int] = Field(0, description="Jumlah pesan dalam session")
    last_activity: Optional[datetime] = None

class SessionHistory(BaseSchema):
    """History conversation dalam session"""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    page: int = Field(1, description="Page number")
    per_page: int = Field(50, description="Messages per page")
    has_more: bool = Field(False, description="Ada lebih banyak messages")

# Extension related schemas
class ExtensionConfig(BaseSchema):
    """Konfigurasi ekstensi"""
    enabled: bool = True
    auto_load: bool = False
    priority: int = Field(0, description="Loading priority")
    settings: Optional[Dict[str, Any]] = None
    api_keys: Optional[Dict[str, str]] = None
    endpoints: Optional[Dict[str, str]] = None
    limits: Optional[Dict[str, Union[int, float]]] = None

class ExtensionInfo(BaseSchema):
    """Informasi ekstensi"""
    name: str = Field(..., description="Nama ekstensi")
    version: str = Field(..., description="Versi ekstensi")
    description: str = Field(..., description="Deskripsi ekstensi")
    author: str = Field(..., description="Author ekstensi")
    extension_type: ExtensionType = Field(..., description="Tipe ekstensi")
    status: ExtensionStatus = Field(ExtensionStatus.INACTIVE)
    dependencies: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    api_endpoints: Optional[List[str]] = None

class ExtensionRequest(BaseSchema):
    """Request untuk extension operations"""
    action: str = Field(..., description="Action yang akan dieksekusi")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter untuk action")
    timeout: Optional[int] = Field(30, ge=1, le=300, description="Timeout dalam detik")
    async_execution: bool = Field(False, description="Execute secara async")

class ExtensionResponse(BaseSchema):
    """Response dari extension operations"""
    name: str
    version: str
    description: str
    author: str
    extension_type: str
    status: str
    loaded: bool = False
    auto_load: bool = False
    dependencies: List[str] = Field(default_factory=list)
    config: Optional[ExtensionConfig] = None
    last_loaded: Optional[datetime] = None
    error_message: Optional[str] = None
    performance_stats: Optional[Dict[str, Any]] = None

class ExtensionExecutionResult(BaseSchema):
    """Result dari extension execution"""
    extension_name: str
    action: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

# Configuration related schemas
class AISettings(BaseSchema):
    """Pengaturan AI"""
    default_model: str = Field("gpt-3.5-turbo", description="Default AI model")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2000, ge=1, le=8000)
    timeout: int = Field(30, ge=1, le=300)
    retry_attempts: int = Field(3, ge=0, le=10)
    api_keys: Optional[Dict[str, str]] = None
    model_configs: Optional[Dict[str, Dict[str, Any]]] = None

class SystemSettings(BaseSchema):
    """Pengaturan sistem"""
    log_level: str = Field("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    max_sessions: int = Field(1000, ge=1)
    session_timeout: int = Field(3600, ge=60)  # seconds
    cleanup_interval: int = Field(300, ge=60)  # seconds
    rate_limit_per_minute: int = Field(60, ge=1)
    max_file_size: int = Field(10485760, ge=1024)  # bytes
    allowed_file_types: List[str] = Field(default_factory=lambda: [".txt", ".pdf", ".docx"])

class ExtensionSettings(BaseSchema):
    """Pengaturan ekstensi"""
    auto_load_extensions: List[str] = Field(default_factory=list)
    extension_timeout: int = Field(30, ge=1, le=300)
    max_concurrent_extensions: int = Field(10, ge=1, le=100)
    extension_configs: Optional[Dict[str, ExtensionConfig]] = None

class APISettings(BaseSchema):
    """Pengaturan API"""
    host: str = Field("localhost")
    port: int = Field(8000, ge=1, le=65535)
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    trusted_hosts: List[str] = Field(default_factory=lambda: ["*"])
    enable_docs: bool = True
    enable_websocket: bool = True
    auth_required: bool = False
    auth_secret_key: Optional[str] = None

class ConfigRequest(BaseSchema):
    """Request untuk update konfigurasi"""
    ai_settings: Optional[AISettings] = None
    system_settings: Optional[SystemSettings] = None
    extension_settings: Optional[ExtensionSettings] = None
    api_settings: Optional[APISettings] = None
    validate_config: bool = Field(True, description="Validate config sebelum save")

class ConfigResponse(BaseSchema):
    """Response konfigurasi"""
    ai_settings: AISettings
    system_settings: SystemSettings
    extension_settings: ExtensionSettings
    api_settings: APISettings
    last_updated: datetime = Field(default_factory=datetime.now)
    config_version: str = "1.0.0"

# Status and Health schemas
class ComponentStatus(BaseSchema):
    """Status komponen sistem"""
    name: str
    status: str  # active, inactive, error
    uptime: Optional[str] = None
    last_check: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class SystemStats(BaseSchema):
    """Statistik sistem"""
    uptime: str
    memory_usage: str
    cpu_usage: Optional[str] = None
    disk_usage: Optional[str] = None
    active_sessions: int = 0
    total_requests: int = 0
    requests_per_minute: float = 0.0
    extensions_loaded: int = 0

class HealthResponse(BaseSchema):
    """Response untuk health check"""
    status: str = "healthy"  # healthy, degraded, unhealthy
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    components: Dict[str, bool] = Field(default_factory=dict)
    checks: Optional[List[ComponentStatus]] = None

class StatusResponse(BaseSchema):
    """Response untuk detailed status"""
    system: SystemStats
    components: Dict[str, ComponentStatus] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    environment: Optional[str] = None

# Memory related schemas
class MemoryStats(BaseSchema):
    """Statistik memory"""
    total_sessions: int = 0
    active_sessions: int = 0
    total_messages: int = 0
    memory_usage_mb: float = 0.0
    oldest_session: Optional[datetime] = None
    newest_session: Optional[datetime] = None
    average_session_size: float = 0.0

class MemoryCleanupResult(BaseSchema):
    """Result dari memory cleanup"""
    sessions_cleaned: int = 0
    messages_cleaned: int = 0
    memory_freed_mb: float = 0.0
    cleanup_duration: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

# File related schemas
class FileInfo(BaseSchema):
    """Informasi file"""
    filename: str
    file_size: int
    file_type: str
    mime_type: str
    upload_time: datetime = Field(default_factory=datetime.now)
    checksum: Optional[str] = None

class FileUploadRequest(BaseSchema):
    """Request untuk file upload"""
    purpose: str = Field(..., description="Tujuan upload file")
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    process_immediately: bool = Field(True)

class FileUploadResponse(BaseSchema):
    """Response file upload"""
    file_id: str
    filename: str
    file_size: int
    upload_status: str  # success, processing, error
    processing_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# WebSocket related schemas
class WebSocketMessage(BaseSchema):
    """Message untuk WebSocket communication"""
    type: str = Field(..., description="Tipe message: chat, command, status")
    session_id: Optional[str] = None
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class WebSocketResponse(BaseSchema):
    """Response untuk WebSocket"""
    type: str
    session_id: Optional[str] = None
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    status: str = "success"  # success, error, processing
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    response_to: Optional[str] = None  # ID of original message

# Error schemas
class ErrorDetail(BaseSchema):
    """Detail error"""
    code: str
    message: str
    field: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseSchema):
    """Response untuk error"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = None
    status_code: int = Field(..., description="HTTP status code")
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None
    trace_id: Optional[str] = None

# Validation schemas
class ValidationError(BaseSchema):
    """Validation error detail"""
    field: str
    message: str
    invalid_value: Optional[Any] = None
    constraint: Optional[str] = None

class ValidationResponse(BaseSchema):
    """Response untuk validation"""
    valid: bool = True
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

# Batch operation schemas
class BatchRequest(BaseSchema):
    """Request untuk batch operations"""
    operations: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    session_id: Optional[str] = None
    fail_on_error: bool = Field(False, description="Stop on first error")
    timeout: int = Field(300, ge=1, le=3600)

class BatchResult(BaseSchema):
    """Result untuk single batch operation"""
    operation_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float

class BatchResponse(BaseSchema):
    """Response untuk batch operations"""
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: List[BatchResult]
    total_time: float
    timestamp: datetime = Field(default_factory=datetime.now)

# Export all schemas
__all__ = [
    # Base
    'BaseSchema',
    
    # Enums
    'ExtensionType', 'ExtensionStatus', 'MessageType', 'SessionStatus',
    
    # Chat
    'ChatMessage', 'ChatContext', 'ChatRequest', 'ChatResponse', 'StreamChunk',
    
    # Session
    'SessionMetadata', 'SessionRequest', 'SessionResponse', 'SessionHistory',
    
    # Extension
    'ExtensionConfig', 'ExtensionInfo', 'ExtensionRequest', 'ExtensionResponse',
    'ExtensionExecutionResult',
    
    # Configuration
    'AISettings', 'SystemSettings', 'ExtensionSettings', 'APISettings',
    'ConfigRequest', 'ConfigResponse',
    
    # Status
    'ComponentStatus', 'SystemStats', 'HealthResponse', 'StatusResponse',
    
    # Memory
    'MemoryStats', 'MemoryCleanupResult',
    
    # File
    'FileInfo', 'FileUploadRequest', 'FileUploadResponse',
    
    # WebSocket
    'WebSocketMessage', 'WebSocketResponse',
    
    # Error
    'ErrorDetail', 'ErrorResponse',
    
    # Validation
    'ValidationError', 'ValidationResponse',
    
    # Batch
    'BatchRequest', 'BatchResult', 'BatchResponse'
]