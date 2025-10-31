"""
Base classes and interfaces for MCP tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ToolParameterType(str, Enum):
    """Enumeration of supported parameter types"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameter(BaseModel):
    """Defines a single tool parameter with type and constraints"""
    type: ToolParameterType
    description: str
    required: bool = True
    enum: Optional[List[str]] = None
    default: Optional[Any] = None
    properties: Optional[Dict[str, "ToolParameter"]] = None
    items: Optional["ToolParameter"] = None


class ToolDefinition(BaseModel):
    """Complete tool definition with metadata and parameters"""
    name: str
    description: str
    parameters: Dict[str, ToolParameter]
    category: str = "general"
    version: str = "1.0.0"


class ToolResult(BaseModel):
    """Standard result structure returned from tool execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool(ABC):
    """Abstract base class that all MCP tools must extend"""
    
    name: str = "base_tool"
    description: str = "Base tool description"
    category: str = "general"
    version: str = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initializes tool with optional configuration"""
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Executes the tool with provided parameters and returns result"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, ToolParameter]:
        """Returns parameter definitions for this tool"""
        pass
    
    def get_definition(self) -> ToolDefinition:
        """Returns complete tool definition including metadata and parameters"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters(),
            category=self.category,
            version=self.version
        )
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates parameters against tool definition before execution"""
        param_defs = self.get_parameters()
        
        for name, param_def in param_defs.items():
            if param_def.required and name not in parameters:
                return False, f"Required parameter '{name}' is missing"
        
        for name, value in parameters.items():
            if name not in param_defs:
                return False, f"Unknown parameter '{name}'"
            
            param_def = param_defs[name]
            if not self._validate_type(value, param_def.type):
                return False, f"Parameter '{name}' has invalid type. Expected {param_def.type}"
        
        return True, None
    
    def _validate_type(self, value: Any, expected_type: ToolParameterType) -> bool:
        """Checks if value matches expected parameter type"""
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
    """Central registry for managing and accessing tool instances"""
    
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
