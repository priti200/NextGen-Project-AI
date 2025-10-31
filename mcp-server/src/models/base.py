"""
Base interfaces for LLM model integrations
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel


class Message(BaseModel):
    """Represents a single message in LLM conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


class ToolCall(BaseModel):
    """Represents a function/tool call made by the LLM"""
    id: str
    type: str = "function"
    function: Dict[str, Any]


class CompletionRequest(BaseModel):
    """Request structure for generating LLM completions"""
    messages: List[Message]
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    stream: bool = False


class CompletionResponse(BaseModel):
    """Response structure containing LLM completion results"""
    model: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: str
    usage: Dict[str, int]
    metadata: Optional[Dict[str, Any]] = None


class BaseModel(ABC):
    """Abstract base class for LLM model integrations"""
    
    def __init__(self, api_key: str, **kwargs):
        """Initializes model with API credentials and configuration"""
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate(
        self,
        request: CompletionRequest
    ) -> CompletionResponse:
        """Generates completion from model based on messages and parameters"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        request: CompletionRequest
    ) -> AsyncIterator[str]:
        """Generates streaming completion, yielding content chunks"""
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Returns whether model supports function/tool calling"""
        pass
    
    @abstractmethod
    def supports_vision(self) -> bool:
        """Returns whether model supports image/vision inputs"""
        pass
    
    @abstractmethod
    def get_max_tokens(self) -> int:
        """Returns maximum token limit for this model"""
        pass
    
    def count_tokens(self, text: str) -> int:
        """Estimates token count using simple heuristic (~4 chars per token)"""
        return len(text) // 4
    
    def format_messages(self, messages: List[Message]) -> Any:
        """Formats messages for model-specific API format (override in subclasses)"""
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def extract_tool_calls(self, response: Any) -> Optional[List[ToolCall]]:
        """Extracts tool calls from raw model response (override in subclasses)"""
        return None


class ModelRegistry:
    """Central registry for managing LLM model instances"""
    
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
