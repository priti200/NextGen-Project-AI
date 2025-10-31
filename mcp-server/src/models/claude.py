"""
Anthropic Claude model integration
"""
from anthropic import AsyncAnthropic
from typing import AsyncIterator, List, Dict, Any, Optional
import json

from .base import (
    BaseModel, CompletionRequest, CompletionResponse,
    Message, ToolCall
)


class ClaudeModel(BaseModel):
    """Anthropic Claude model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, **kwargs)
        
        self.model_name = model_name
        self.client = AsyncAnthropic(api_key=api_key)
        
        # Model capabilities
        self._supports_vision = "claude-3" in model_name
        self._supports_tools = True
        
        # Token limits
        self._max_tokens_map = {
            "claude-3-opus": 4096,
            "claude-3-sonnet": 4096,
            "claude-3-haiku": 4096,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
        }
        
        # Find matching model
        self._max_tokens = 4096
        for key, value in self._max_tokens_map.items():
            if key in model_name:
                self._max_tokens = value
                break
    
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """
        Generate completion using Claude
        
        Args:
            request: Completion request
            
        Returns:
            CompletionResponse with generated content
        """
        try:
            # Separate system message from other messages
            system_message = None
            formatted_messages = []
            
            for msg in request.messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "max_tokens": request.max_tokens or 2048,
                "temperature": request.temperature or 0.7,
            }
            
            # Add system message if present
            if system_message:
                params["system"] = system_message
            
            # Add tools if provided
            if request.tools and self._supports_tools:
                params["tools"] = self._convert_tools_to_claude(request.tools)
            
            # Generate response
            response = await self.client.messages.create(**params)
            
            # Extract content and tool calls
            content = None
            tool_calls = None
            
            for block in response.content:
                if block.type == "text":
                    content = block.text
                elif block.type == "tool_use":
                    if not tool_calls:
                        tool_calls = []
                    tool_calls.append(
                        ToolCall(
                            id=block.id,
                            type="function",
                            function={
                                "name": block.name,
                                "arguments": json.dumps(block.input)
                            }
                        )
                    )
            
            # Map stop reason
            finish_reason_map = {
                "end_turn": "stop",
                "max_tokens": "length",
                "tool_use": "tool_calls",
                "stop_sequence": "stop"
            }
            finish_reason = finish_reason_map.get(response.stop_reason, "stop")
            
            return CompletionResponse(
                model=response.model,
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                metadata={
                    "provider": "anthropic",
                    "model_version": response.model,
                    "stop_reason": response.stop_reason
                }
            )
            
        except Exception as e:
            raise Exception(f"Claude generation failed: {str(e)}")
    
    async def generate_stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """
        Generate streaming completion using Claude
        
        Args:
            request: Completion request
            
        Yields:
            Chunks of generated content
        """
        try:
            # Separate system message from other messages
            system_message = None
            formatted_messages = []
            
            for msg in request.messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "messages": formatted_messages,
                "max_tokens": request.max_tokens or 2048,
                "temperature": request.temperature or 0.7,
                "stream": True
            }
            
            # Add system message if present
            if system_message:
                params["system"] = system_message
            
            # Generate streaming response
            async with self.client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise Exception(f"Claude streaming failed: {str(e)}")
    
    def supports_tools(self) -> bool:
        """Check if model supports tool/function calling"""
        return self._supports_tools
    
    def supports_vision(self) -> bool:
        """Check if model supports vision/image inputs"""
        return self._supports_vision
    
    def get_max_tokens(self) -> int:
        """Get maximum token limit for this model"""
        return self._max_tokens
    
    def _convert_tools_to_claude(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI-style tools to Claude format
        
        Claude uses a slightly different tool format
        """
        claude_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                claude_tools.append({
                    "name": func.get("name"),
                    "description": func.get("description"),
                    "input_schema": func.get("parameters", {})
                })
        
        return claude_tools
