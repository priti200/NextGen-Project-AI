"""
Base model interface for LLM integrations
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel


class Message(BaseModel):
    """Message structure for LLM conversations"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


class ToolCall(BaseModel):
    """Tool call structure"""
    id: str
    type: str = "function"
    function: Dict[str, Any]


class CompletionRequest(BaseModel):
    """Request structure for LLM completion"""
    messages: List[Message]
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    stream: bool = False


class CompletionResponse(BaseModel):
    """Response structure for LLM completion"""
    model: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: str
    usage: Dict[str, int]
    metadata: Optional[Dict[str, Any]] = None


class BaseModel(ABC):
    """Base class for all LLM model integrations"""
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the model
        
        Args:
            api_key: API key for the model provider
            **kwargs: Additional configuration options
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """
        Generate completion from the model
        
        Args:
            request: Completion request with messages and parameters
            
        Returns:
            CompletionResponse with generated content
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """
        Generate streaming completion from the model
        
        Args:
            request: Completion request with messages and parameters
            
        Yields:
            Chunks of generated content
        """
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if model supports tool/function calling"""
        pass
    
    @abstractmethod
    def supports_vision(self) -> bool:
        """Check if model supports vision/image inputs"""
        pass
    
    @abstractmethod
    def get_max_tokens(self) -> int:
        """Get maximum token limit for this model"""
        pass
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def format_messages(self, messages: List[Message]) -> Any:
        """
        Format messages for the specific model API
        
        Args:
            messages: List of messages
            
        Returns:
            Formatted messages for the model
        """
        # Default implementation - override in subclasses
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def extract_tool_calls(self, response: Any) -> Optional[List[ToolCall]]:
        """
        Extract tool calls from model response
        
        Args:
            response: Raw model response
            
        Returns:
            List of tool calls if present
        """
        # Default implementation - override in subclasses
        return None


class ModelRegistry:
    """Registry for managing model instances"""
    
    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
    
    def register(self, name: str, model: BaseModel):
        """Register a model instance"""
        self._models[name] = model
    
    def get(self, name: str) -> Optional[BaseModel]:
        """Get a registered model by name"""
        return self._models.get(name)
    
    def list_models(self) -> List[str]:
        """List all registered model names"""
        return list(self._models.keys())
    
    def unregister(self, name: str):
        """Unregister a model"""
        if name in self._models:
            del self._models[name]


# Global model registry instance
model_registry = ModelRegistry()
