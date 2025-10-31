"""
Custom/Open-source model integration
Supports any OpenAI-compatible API endpoint
"""
from openai import AsyncOpenAI
from typing import AsyncIterator, List, Dict, Any, Optional
import httpx

from .base import (
    BaseModel, CompletionRequest, CompletionResponse,
    Message, ToolCall
)


class CustomModel(BaseModel):
    """
    Custom model implementation for self-hosted or open-source models
    
    Supports any OpenAI-compatible API including:
    - Local LLMs (Ollama, LM Studio, LocalAI)
    - Self-hosted models (vLLM, TGI, FastChat)
    - Custom fine-tuned models
    - Other providers with OpenAI-compatible APIs
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str,
        model_name: str,
        supports_tools: bool = False,
        supports_vision: bool = False,
        max_tokens: int = 4096,
        **kwargs
    ):
        """
        Initialize custom model
        
        Args:
            api_key: API key (use "dummy" for local models that don't need auth)
            base_url: Base URL of the API endpoint (e.g., http://localhost:11434/v1)
            model_name: Model name to use in API calls
            supports_tools: Whether the model supports function calling
            supports_vision: Whether the model supports image inputs
            max_tokens: Maximum token limit
        """
        super().__init__(api_key, **kwargs)
        
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self._supports_tools = supports_tools
        self._supports_vision = supports_vision
        self._max_tokens = max_tokens
        
        # Create custom HTTP client with longer timeouts for local models
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=300.0,  # 5 minutes for generation
                write=10.0,
                pool=10.0
            )
        )
        
        # Initialize OpenAI client with custom base URL
        self.client = AsyncOpenAI(
            api_key=api_key if api_key else "dummy",
            base_url=self.base_url,
            http_client=http_client
        )
    
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """
        Generate completion using custom model
        
        Args:
            request: Completion request
            
        Returns:
            CompletionResponse with generated content
        """
        try:
            # Format messages
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or self._max_tokens,
            }
            
            # Add tools if supported
            if request.tools and self._supports_tools:
                params["tools"] = request.tools
                if request.tool_choice:
                    params["tool_choice"] = request.tool_choice
            
            # Generate response
            response = await self.client.chat.completions.create(**params)
            
            # Extract content and tool calls
            choice = response.choices[0]
            content = choice.message.content
            tool_calls = None
            
            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        type=tc.type,
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    )
                    for tc in choice.message.tool_calls
                ]
            
            # Handle token usage (might not be available for all custom models)
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
            
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens or 0,
                    "completion_tokens": response.usage.completion_tokens or 0,
                    "total_tokens": response.usage.total_tokens or 0
                }
            
            return CompletionResponse(
                model=self.model_name,
                content=content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason or "stop",
                usage=usage,
                metadata={
                    "provider": "custom",
                    "base_url": self.base_url,
                    "model_name": self.model_name
                }
            )
            
        except Exception as e:
            raise Exception(f"Custom model generation failed: {str(e)}")
    
    async def generate_stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """
        Generate streaming completion using custom model
        
        Args:
            request: Completion request
            
        Yields:
            Chunks of generated content
        """
        try:
            # Format messages
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or self._max_tokens,
                "stream": True
            }
            
            # Add tools if supported
            if request.tools and self._supports_tools:
                params["tools"] = request.tools
            
            # Generate streaming response
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"Custom model streaming failed: {str(e)}")
    
    def supports_tools(self) -> bool:
        """Check if model supports tool/function calling"""
        return self._supports_tools
    
    def supports_vision(self) -> bool:
        """Check if model supports vision/image inputs"""
        return self._supports_vision
    
    def get_max_tokens(self) -> int:
        """Get maximum token limit for this model"""
        return self._max_tokens


class OllamaModel(CustomModel):
    """
    Specialized adapter for Ollama
    
    Ollama is a popular local LLM runner with OpenAI-compatible API
    Default endpoint: http://localhost:11434/v1
    """
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434/v1", **kwargs):
        super().__init__(
            api_key="dummy",  # Ollama doesn't require auth
            base_url=base_url,
            model_name=model_name,
            supports_tools=False,  # Most Ollama models don't support tools yet
            supports_vision=model_name in ["llava", "bakllava"],
            max_tokens=kwargs.get("max_tokens", 4096),
            **kwargs
        )


class LMStudioModel(CustomModel):
    """
    Specialized adapter for LM Studio
    
    LM Studio provides OpenAI-compatible API for local models
    Default endpoint: http://localhost:1234/v1
    """
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:1234/v1", **kwargs):
        super().__init__(
            api_key="lm-studio",  # LM Studio accepts any key
            base_url=base_url,
            model_name=model_name,
            supports_tools=kwargs.get("supports_tools", False),
            supports_vision=kwargs.get("supports_vision", False),
            max_tokens=kwargs.get("max_tokens", 4096),
            **kwargs
        )


class LocalAIModel(CustomModel):
    """
    Specialized adapter for LocalAI
    
    LocalAI is a drop-in replacement REST API compatible with OpenAI
    Default endpoint: http://localhost:8080/v1
    """
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:8080/v1", **kwargs):
        super().__init__(
            api_key="dummy",  # LocalAI doesn't require auth by default
            base_url=base_url,
            model_name=model_name,
            supports_tools=kwargs.get("supports_tools", False),
            supports_vision=kwargs.get("supports_vision", False),
            max_tokens=kwargs.get("max_tokens", 4096),
            **kwargs
        )
