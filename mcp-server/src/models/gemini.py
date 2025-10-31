"""
Google Gemini model integration
"""
import google.generativeai as genai
from typing import AsyncIterator, List, Dict, Any, Optional
import json

from .base import (
    BaseModel, CompletionRequest, CompletionResponse, 
    Message, ToolCall
)


class GeminiModel(BaseModel):
    """Google Gemini model implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", **kwargs):
        super().__init__(api_key, **kwargs)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Model capabilities
        self._supports_vision = "vision" in model_name.lower()
        self._supports_tools = True
        self._max_tokens = kwargs.get("max_tokens", 2048)
    
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """
        Generate completion using Gemini
        
        Args:
            request: Completion request
            
        Returns:
            CompletionResponse with generated content
        """
        try:
            # Format messages for Gemini
            formatted_messages = self._format_messages_for_gemini(request.messages)
            
            # Prepare generation config
            generation_config = {
                "temperature": request.temperature or 0.7,
                "max_output_tokens": request.max_tokens or self._max_tokens,
            }
            
            # Convert tools if provided
            tools_config = None
            if request.tools and self._supports_tools:
                tools_config = self._convert_tools_to_gemini(request.tools)
            
            # Generate response
            if tools_config:
                response = self.model.generate_content(
                    formatted_messages,
                    generation_config=generation_config,
                    tools=tools_config
                )
            else:
                response = self.model.generate_content(
                    formatted_messages,
                    generation_config=generation_config
                )
            
            # Extract content and tool calls
            content = None
            tool_calls = None
            
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        content = part.text
                    elif hasattr(part, 'function_call'):
                        if not tool_calls:
                            tool_calls = []
                        tool_calls.append(
                            ToolCall(
                                id=f"call_{len(tool_calls)}",
                                type="function",
                                function={
                                    "name": part.function_call.name,
                                    "arguments": json.dumps(dict(part.function_call.args))
                                }
                            )
                        )
            
            # Calculate token usage (Gemini doesn't provide exact counts)
            prompt_tokens = sum(self.count_tokens(msg.content) for msg in request.messages)
            completion_tokens = self.count_tokens(content) if content else 0
            
            return CompletionResponse(
                model=self.model_name,
                content=content,
                tool_calls=tool_calls,
                finish_reason="stop" if content else "tool_calls",
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                metadata={
                    "provider": "google",
                    "model_version": self.model_name
                }
            )
            
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")
    
    async def generate_stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """
        Generate streaming completion using Gemini
        
        Args:
            request: Completion request
            
        Yields:
            Chunks of generated content
        """
        try:
            # Format messages for Gemini
            formatted_messages = self._format_messages_for_gemini(request.messages)
            
            # Prepare generation config
            generation_config = {
                "temperature": request.temperature or 0.7,
                "max_output_tokens": request.max_tokens or self._max_tokens,
            }
            
            # Generate streaming response
            response = self.model.generate_content(
                formatted_messages,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise Exception(f"Gemini streaming failed: {str(e)}")
    
    def supports_tools(self) -> bool:
        """Check if model supports tool/function calling"""
        return self._supports_tools
    
    def supports_vision(self) -> bool:
        """Check if model supports vision/image inputs"""
        return self._supports_vision
    
    def get_max_tokens(self) -> int:
        """Get maximum token limit for this model"""
        return self._max_tokens
    
    def _format_messages_for_gemini(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format messages for Gemini API
        
        Gemini uses a different format than OpenAI
        """
        formatted = []
        
        for msg in messages:
            if msg.role == "system":
                # Gemini doesn't have system role, prepend to first user message
                if not formatted:
                    formatted.append({
                        "role": "user",
                        "parts": [{"text": f"System: {msg.content}"}]
                    })
                else:
                    # Prepend to existing first message
                    formatted[0]["parts"][0]["text"] = f"System: {msg.content}\n\n{formatted[0]['parts'][0]['text']}"
            elif msg.role == "user":
                formatted.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == "assistant":
                formatted.append({
                    "role": "model",  # Gemini uses "model" instead of "assistant"
                    "parts": [{"text": msg.content}]
                })
        
        return formatted
    
    def _convert_tools_to_gemini(self, tools: List[Dict[str, Any]]) -> List[Any]:
        """Convert OpenAI-style tools to Gemini function declarations"""
        gemini_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                gemini_tools.append(
                    genai.protos.FunctionDeclaration(
                        name=func.get("name"),
                        description=func.get("description"),
                        parameters=func.get("parameters", {})
                    )
                )
        
        return [genai.protos.Tool(function_declarations=gemini_tools)] if gemini_tools else None
