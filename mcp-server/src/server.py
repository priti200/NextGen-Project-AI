"""
MCP Server - Main FastAPI application
Model Context Protocol server with multi-LLM support
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from config import get_settings, get_model_config
from models.base import (
    CompletionRequest, CompletionResponse, 
    model_registry, Message
)
from models.factory import initialize_models
from tools.base import tool_registry, ToolResult
from utils.logger import setup_logging, get_logger

# Initialize settings and logger
settings = get_settings()
logger = get_logger(__name__)


# Pydantic models for API
class InitializeRequest(BaseModel):
    """MCP initialize request"""
    protocol_version: str = "1.0"
    client_info: Dict[str, str]
    capabilities: Optional[Dict[str, Any]] = None


class InitializeResponse(BaseModel):
    """MCP initialize response"""
    session_id: str
    protocol_version: str
    server_info: Dict[str, str]
    capabilities: Dict[str, Any]


class ToolCallRequest(BaseModel):
    """Request to call a tool"""
    session_id: str
    name: str
    parameters: Dict[str, Any]


class ToolListResponse(BaseModel):
    """Response with list of available tools"""
    tools: List[Dict[str, Any]]


class CompletionRequestAPI(BaseModel):
    """API request for LLM completion"""
    session_id: Optional[str] = None
    model: Optional[str] = None
    messages: List[Message]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    tools: Optional[List[Dict[str, Any]]] = None
    stream: bool = False


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    models_available: List[str]
    tools_available: int


# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting MCP Server", 
                host=settings.mcp_server_host, 
                port=settings.mcp_server_port)
    
    # Initialize LLM models
    logger.info("Initializing LLM models...")
    initialize_models()
    
    # Initialize tools (will be implemented in next task)
    logger.info("Initializing tools...")
    
    logger.info("MCP Server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP Server")
    sessions.clear()


# Create FastAPI app
app = FastAPI(
    title="NextGen Project AI - MCP Server",
    description="Model Context Protocol server with multi-LLM support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        models_available=model_registry.list_models(),
        tools_available=len(tool_registry.list_tools())
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NextGen Project AI - MCP Server",
        "version": "1.0.0",
        "protocol": "Model Context Protocol",
        "status": "running",
        "docs": "/docs"
    }


# ============================================================================
# MCP Protocol Endpoints
# ============================================================================

@app.post("/mcp/initialize", response_model=InitializeResponse)
async def initialize_session(request: InitializeRequest):
    """
    Initialize a new MCP session
    
    Creates a new session and returns session ID with server capabilities
    """
    session_id = str(uuid.uuid4())
    
    # Store session info
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


@app.post("/mcp/tools/list", response_model=ToolListResponse)
async def list_tools(session_id: Optional[str] = None):
    """
    List all available tools
    
    Returns list of tools with their definitions and parameters
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


@app.post("/mcp/tools/call", response_model=ToolResult)
async def call_tool(request: ToolCallRequest):
    """
    Execute a tool
    
    Validates parameters and executes the specified tool
    """
    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get tool
    tool = tool_registry.get(request.name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{request.name}' not found"
        )
    
    # Validate parameters
    is_valid, error_msg = tool.validate_parameters(request.parameters)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Execute tool
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


@app.post("/mcp/completion", response_model=CompletionResponse)
async def generate_completion(request: CompletionRequestAPI):
    """
    Generate LLM completion
    
    Processes messages and generates response using specified model
    """
    # Select model
    model_name = request.model or settings.default_model
    
    # Validate model is configured
    if not settings.validate_model_config(model_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{model_name}' is not configured. Please set API key."
        )
    
    # Get model instance
    model = model_registry.get(model_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_name}' not found"
        )
    
    # Create completion request
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
        
        # Generate completion
        response = await model.generate(completion_request)
        
        # Update session context if session_id provided
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


@app.get("/mcp/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
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


@app.delete("/mcp/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
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
    """Global exception handler"""
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
    
    # Setup logging
    setup_logging(
        log_level=settings.mcp_log_level,
        log_file="logs/mcp_server.log" if not settings.mcp_debug else None,
        json_logs=False
    )
    
    # Run server
    uvicorn.run(
        "server:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=settings.mcp_debug,
        workers=1 if settings.mcp_debug else settings.mcp_workers,
        log_level=settings.mcp_log_level.lower()
    )
