"""
Base tool interface for MCP tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ToolParameterType(str, Enum):
    """Supported parameter types for tools"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    type: ToolParameterType
    description: str
    required: bool = True
    enum: Optional[List[str]] = None
    default: Optional[Any] = None
    properties: Optional[Dict[str, "ToolParameter"]] = None
    items: Optional["ToolParameter"] = None


class ToolDefinition(BaseModel):
    """Tool definition for MCP protocol"""
    name: str
    description: str
    parameters: Dict[str, ToolParameter]
    category: str = "general"
    version: str = "1.0.0"


class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Base class for all MCP tools"""
    
    # These should be overridden in subclasses
    name: str = "base_tool"
    description: str = "Base tool description"
    category: str = "general"
    version: str = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the tool
        
        Args:
            config: Tool-specific configuration
        """
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given parameters
        
        Args:
            parameters: Tool parameters
            
        Returns:
            ToolResult with execution results
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, ToolParameter]:
        """
        Get tool parameter definitions
        
        Returns:
            Dictionary of parameter definitions
        """
        pass
    
    def get_definition(self) -> ToolDefinition:
        """
        Get complete tool definition
        
        Returns:
            ToolDefinition for this tool
        """
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters(),
            category=self.category,
            version=self.version
        )
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters before execution
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        param_defs = self.get_parameters()
        
        # Check required parameters
        for name, param_def in param_defs.items():
            if param_def.required and name not in parameters:
                return False, f"Required parameter '{name}' is missing"
        
        # Check parameter types
        for name, value in parameters.items():
            if name not in param_defs:
                return False, f"Unknown parameter '{name}'"
            
            param_def = param_defs[name]
            if not self._validate_type(value, param_def.type):
                return False, f"Parameter '{name}' has invalid type. Expected {param_def.type}"
        
        return True, None
    
    def _validate_type(self, value: Any, expected_type: ToolParameterType) -> bool:
        """Validate value type"""
        type_map = {
            ToolParameterType.STRING: str,
            ToolParameterType.NUMBER: (int, float),
            ToolParameterType.INTEGER: int,
            ToolParameterType.BOOLEAN: bool,
            ToolParameterType.OBJECT: dict,
            ToolParameterType.ARRAY: list,
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True


class ToolRegistry:
    """Registry for managing tool instances"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool instance"""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a registered tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tool definitions"""
        return [tool.get_definition() for tool in self._tools.values()]
    
    def get_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a specific category"""
        return [tool for tool in self._tools.values() if tool.category == category]
    
    def unregister(self, name: str):
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]


# Global tool registry instance
tool_registry = ToolRegistry()
