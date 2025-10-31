"""
MCP Server - FastAPI implementation of Model Context Protocol
Multi-LLM support with integrated tools for project management and analysis
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
import time
import psutil
import sys

from config import get_settings, get_model_config
from models.base import (
    CompletionRequest, CompletionResponse, 
    model_registry, Message
)
from models.factory import initialize_models
from tools.base import tool_registry, ToolResult
from tools.factory import initialize_tools
from utils.logger import setup_logging, get_logger
from middleware.security import rate_limit_middleware, security_headers_middleware

settings = get_settings()
logger = get_logger(__name__)

# Server state tracking
server_state = {
    "startup_time": None,
    "is_ready": False,
    "total_requests": 0,
    "failed_requests": 0
}


class InitializeRequest(BaseModel):
    """Request model for MCP session initialization"""
    protocol_version: str = "1.0"
    client_info: Dict[str, str]
    capabilities: Optional[Dict[str, Any]] = None


class InitializeResponse(BaseModel):
    """Response model for MCP session initialization"""
    session_id: str
    protocol_version: str
    server_info: Dict[str, str]
    capabilities: Dict[str, Any]


class ToolCallRequest(BaseModel):
    """Request model for tool execution"""
    session_id: str
    name: str
    parameters: Dict[str, Any]


class ToolListResponse(BaseModel):
    """Response model with available tools listing"""
    tools: List[Dict[str, Any]]


class CompletionRequestAPI(BaseModel):
    """Request model for LLM completion generation"""
    session_id: Optional[str] = None
    model: Optional[str] = None
    messages: List[Message]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    tools: Optional[List[Dict[str, Any]]] = None
    stream: bool = False


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    timestamp: str
    version: str
    models_available: List[str]
    tools_available: int


class ReadinessResponse(BaseModel):
    """Response model for readiness probe"""
    ready: bool
    services: Dict[str, str]
    uptime_seconds: float


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    uptime_seconds: float
    total_requests: int
    failed_requests: int
    success_rate: float
    memory_usage_mb: float
    cpu_percent: float
    active_sessions: int


# In-memory session storage (use Redis/database for production)
sessions: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown lifecycle"""
    server_state["startup_time"] = time.time()
    
    logger.info("Starting MCP Server", 
                host=settings.mcp_server_host, 
                port=settings.mcp_server_port)
    
    try:
        logger.info("Initializing LLM models...")
        initialize_models()
        
        logger.info("Initializing tools...")
        tools_config = {
            "jira_api_url": settings.jira_api_url,
            "jira_api_token": settings.jira_api_token,
            "jira_email": settings.jira_email,
            "github_token": settings.github_token,
            "github_api_url": settings.github_api_url,
            "ml_service_url": settings.ml_service_url
        }
        initialize_tools(tools_config)
        
        server_state["is_ready"] = True
        logger.info("MCP Server started successfully")
        
    except Exception as e:
        logger.error("Failed to initialize MCP Server", error=str(e))
        server_state["is_ready"] = False
        raise
    
    yield
    
    logger.info("Shutting down MCP Server gracefully")
    server_state["is_ready"] = False
    
    # Cleanup resources
    sessions.clear()
    logger.info("Server shutdown complete")


app = FastAPI(
    title="NextGen Project AI - MCP Server",
    description="Model Context Protocol server with multi-LLM support and integrated tools for project management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    server_state["total_requests"] += 1
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            server_state["failed_requests"] += 1
        return response
    except Exception as e:
        server_state["failed_requests"] += 1
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    return await security_headers_middleware(request, call_next)

@app.middleware("http")
async def add_rate_limiting(request: Request, call_next):
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/ready", "/metrics"]:
        return await call_next(request)
    return await rate_limit_middleware(request, call_next)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns basic server health and available resources.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        models_available=model_registry.list_models(),
        tools_available=len(tool_registry.list_tools())
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness probe for Kubernetes and orchestration systems.
    Indicates if server is ready to accept requests.
    """
    uptime = time.time() - server_state["startup_time"] if server_state["startup_time"] else 0
    
    services_status = {
        "models": "ready" if len(model_registry.list_models()) > 0 else "not_ready",
        "tools": "ready" if len(tool_registry.list_tools()) > 0 else "not_ready",
        "server": "ready" if server_state["is_ready"] else "not_ready"
    }
    
    all_ready = all(status == "ready" for status in services_status.values())
    
    return ReadinessResponse(
        ready=all_ready,
        services=services_status,
        uptime_seconds=round(uptime, 2)
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def metrics():
    """
    Metrics endpoint for monitoring systems (Prometheus compatible).
    Returns operational metrics and resource usage.
    """
    uptime = time.time() - server_state["startup_time"] if server_state["startup_time"] else 0
    total_requests = server_state["total_requests"]
    failed_requests = server_state["failed_requests"]
    success_rate = ((total_requests - failed_requests) / total_requests * 100) if total_requests > 0 else 100.0
    
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent(interval=0.1)
    
    return MetricsResponse(
        uptime_seconds=round(uptime, 2),
        total_requests=total_requests,
        failed_requests=failed_requests,
        success_rate=round(success_rate, 2),
        memory_usage_mb=round(memory_mb, 2),
        cpu_percent=round(cpu_percent, 2),
        active_sessions=len(sessions)
    )


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with service information and documentation links"""
    return {
        "service": "NextGen Project AI - MCP Server",
        "version": "1.0.0",
        "protocol": "Model Context Protocol",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics"
    }


# ============================================================================
# MCP Protocol Endpoints
# ============================================================================

@app.post("/mcp/initialize", response_model=InitializeResponse, tags=["MCP Protocol"])
async def initialize_session(request: InitializeRequest):
    """
    Initialize a new MCP session.
    
    Creates a new session with unique ID and returns server capabilities.
    This should be the first call when establishing a connection.
    """
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "created_at": datetime.utcnow().isoformat(),
        "client_info": request.client_info,
        "protocol_version": request.protocol_version,
        "context": [],
        "metadata": {}
    }
    
    logger.info("New session initialized", 
                session_id=session_id, 
                client=request.client_info.get("name"))
    
    return InitializeResponse(
        session_id=session_id,
        protocol_version="1.0",
        server_info={
            "name": "NextGen MCP Server",
            "version": "1.0.0",
            "vendor": "Team EigenFlow"
        },
        capabilities={
            "tools": True,
            "prompts": True,
            "resources": True,
            "streaming": True,
            "multi_model": True
        }
    )


@app.post("/mcp/tools/list", response_model=ToolListResponse, tags=["MCP Protocol", "Tools"])
async def list_tools(session_id: Optional[str] = None):
    """
    List all available tools.
    
    Returns comprehensive list of tools with their parameters, descriptions,
    and requirements. Use this to discover available capabilities.
    """
    tools = tool_registry.list_tools()
    
    return ToolListResponse(
        tools=[
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "version": tool.version,
                "parameters": {
                    name: {
                        "type": param.type,
                        "description": param.description,
                        "required": param.required
                    }
                    for name, param in tool.parameters.items()
                }
            }
            for tool in tools
        ]
    )


@app.post("/mcp/tools/call", response_model=ToolResult, tags=["MCP Protocol", "Tools"])
async def call_tool(request: ToolCallRequest):
    """
    Execute a specific tool.
    
    Calls the specified tool with provided parameters after validation.
    Returns execution results or error information.
    """
    if request.session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    tool = tool_registry.get(request.name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{request.name}' not found"
        )
    
    is_valid, error_msg = tool.validate_parameters(request.parameters)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    try:
        logger.info("Executing tool", 
                   tool_name=request.name, 
                   session_id=request.session_id)
        
        result = await tool.execute(request.parameters)
        
        logger.info("Tool execution completed", 
                   tool_name=request.name, 
                   success=result.success)
        
        return result
        
    except Exception as e:
        logger.error("Tool execution failed", 
                    tool_name=request.name, 
                    error=str(e))
        
        return ToolResult(
            success=False,
            error=str(e)
        )


@app.post("/mcp/completion", response_model=CompletionResponse, tags=["MCP Protocol", "LLM"])
async def generate_completion(request: CompletionRequestAPI):
    """
    Generate LLM completion.
    
    Processes messages through specified LLM model and returns generated response.
    Supports tool calling, streaming, and context management.
    """
    model_name = request.model or settings.default_model
    
    if not settings.validate_model_config(model_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{model_name}' is not configured. Please set API key."
        )
    
    model = model_registry.get(model_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_name}' not found"
        )
    
    completion_request = CompletionRequest(
        messages=request.messages,
        model=model_name,
        max_tokens=request.max_tokens or settings.max_tokens,
        temperature=request.temperature or settings.temperature,
        tools=request.tools,
        stream=request.stream
    )
    
    try:
        logger.info("Generating completion", 
                   model=model_name, 
                   messages_count=len(request.messages))
        
        response = await model.generate(completion_request)
        
        if request.session_id and request.session_id in sessions:
            sessions[request.session_id]["context"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "messages": [msg.dict() for msg in request.messages],
                "response": response.dict()
            })
        
        logger.info("Completion generated", 
                   model=model_name, 
                   finish_reason=response.finish_reason)
        
        return response
        
    except Exception as e:
        logger.error("Completion generation failed", 
                    model=model_name, 
                    error=str(e))
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate completion: {str(e)}"
        )


@app.get("/mcp/session/{session_id}", tags=["MCP Protocol", "Session"])
async def get_session(session_id: str):
    """
    Get session information.
    
    Retrieves details about a specific session including creation time,
    client info, and context length.
    """
    if session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "client_info": session["client_info"],
        "context_length": len(session["context"])
    }


@app.delete("/mcp/session/{session_id}", tags=["MCP Protocol", "Session"])
async def delete_session(session_id: str):
    """
    Delete a session.
    
    Removes session and clears all associated context and data.
    Use this for cleanup when session is no longer needed.
    """
    if session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    del sessions[session_id]
    logger.info("Session deleted", session_id=session_id)
    
    return {"message": "Session deleted successfully"}


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handles all unhandled exceptions with logging"""
    logger.error("Unhandled exception", 
                error=str(exc), 
                path=str(request.url))
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.mcp_debug else "An error occurred"
        }
    )


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import signal
    
    setup_logging(
        log_level=settings.mcp_log_level,
        log_file="logs/mcp_server.log" if not settings.mcp_debug else None,
        json_logs=False
    )
    
    # Graceful shutdown handler
    def handle_shutdown(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        server_state["is_ready"] = False
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    logger.info("Starting MCP Server with graceful shutdown support")
    
    uvicorn.run(
        "server:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=settings.mcp_debug,
        workers=1 if settings.mcp_debug else settings.mcp_workers,
        log_level=settings.mcp_log_level.lower()
    )
