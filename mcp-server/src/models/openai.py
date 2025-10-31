"""
OpenAI GPT model integration
"""
from openai import AsyncOpenAI
from typing import AsyncIterator, List, Dict, Any, Optional
import json

from .base import (
    BaseModel, CompletionRequest, CompletionResponse,
    Message, ToolCall
)


class OpenAIModel(BaseModel):
    """OpenAI GPT model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4", **kwargs):
        super().__init__(api_key, **kwargs)
        
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Model capabilities based on model name
        self._supports_vision = "vision" in model_name or "gpt-4" in model_name
        self._supports_tools = True
        
        # Token limits by model
        self._max_tokens_map = {
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
        }
        self._max_tokens = self._max_tokens_map.get(model_name, 4096)
    
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """
        Generate completion using OpenAI
        
        Args:
            request: Completion request
            
        Returns:
            CompletionResponse with generated content
        """
        try:
            # Format messages for OpenAI
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 2048,
            }
            
            # Add tools if provided
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
            
            if choice.message.tool_calls:
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
            
            return CompletionResponse(
                model=response.model,
                content=content,
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                metadata={
                    "provider": "openai",
                    "model_version": response.model,
                    "system_fingerprint": response.system_fingerprint
                }
            )
            
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    async def generate_stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """
        Generate streaming completion using OpenAI
        
        Args:
            request: Completion request
            
        Yields:
            Chunks of generated content
        """
        try:
            # Format messages for OpenAI
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 2048,
                "stream": True
            }
            
            # Add tools if provided
            if request.tools and self._supports_tools:
                params["tools"] = request.tools
            
            # Generate streaming response
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI streaming failed: {str(e)}")
    
    def supports_tools(self) -> bool:
        """Check if model supports tool/function calling"""
        return self._supports_tools
    
    def supports_vision(self) -> bool:
        """Check if model supports vision/image inputs"""
        return self._supports_vision
    
    def get_max_tokens(self) -> int:
        """Get maximum token limit for this model"""
        return self._max_tokens
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count using tiktoken (more accurate for OpenAI)
        
        Note: For production, install tiktoken package
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to simple estimation
            return super().count_tokens(text)
