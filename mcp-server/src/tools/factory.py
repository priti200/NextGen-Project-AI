"""
Tool Factory
Initializes and registers all MCP tools
"""
from typing import Dict, Optional
import structlog

from .base import tool_registry
from .project_analyzer import ProjectAnalyzerTool
from .risk_predictor import RiskPredictorTool
from .code_analyzer import CodeAnalyzerTool
from .jira_integration import JiraIntegrationTool
from .github_integration import GitHubIntegrationTool

logger = structlog.get_logger()


def initialize_tools(config: Optional[Dict] = None):
    """
    Initialize and register all MCP tools
    
    Args:
        config: Configuration dictionary containing API keys and URLs
    """
    logger.info("Initializing MCP tools...")
    
    # Use the global tool registry singleton
    registry = tool_registry
    tools_config = {}
    
    if config:
        # Extract tool-related configuration
        tools_config = {
            "jira_api_url": config.get("jira_api_url"),
            "jira_api_token": config.get("jira_api_token"),
            "jira_email": config.get("jira_email"),
            "github_token": config.get("github_token"),
            "github_api_url": config.get("github_api_url", "https://api.github.com"),
            "ml_service_url": config.get("ml_service_url")
        }
    
    # Initialize and register tools
    tools_initialized = 0
    
    try:
        # Project Analyzer
        project_analyzer = ProjectAnalyzerTool(tools_config)
        registry.register(project_analyzer)
        tools_initialized += 1
        logger.info("Registered ProjectAnalyzerTool")
    except Exception as e:
        logger.error(f"Failed to initialize ProjectAnalyzerTool: {e}")
    
    try:
        # Risk Predictor
        risk_predictor = RiskPredictorTool(tools_config)
        registry.register(risk_predictor)
        tools_initialized += 1
        logger.info("Registered RiskPredictorTool")
    except Exception as e:
        logger.error(f"Failed to initialize RiskPredictorTool: {e}")
    
    try:
        # Code Analyzer
        code_analyzer = CodeAnalyzerTool(tools_config)
        registry.register(code_analyzer)
        tools_initialized += 1
        logger.info("Registered CodeAnalyzerTool")
    except Exception as e:
        logger.error(f"Failed to initialize CodeAnalyzerTool: {e}")
    
    try:
        # Jira Integration
        jira_integration = JiraIntegrationTool(tools_config)
        registry.register(jira_integration)
        tools_initialized += 1
        logger.info("Registered JiraIntegrationTool")
    except Exception as e:
        logger.error(f"Failed to initialize JiraIntegrationTool: {e}")
    
    try:
        # GitHub Integration
        github_integration = GitHubIntegrationTool(tools_config)
        registry.register(github_integration)
        tools_initialized += 1
        logger.info("Registered GitHubIntegrationTool")
    except Exception as e:
        logger.error(f"Failed to initialize GitHubIntegrationTool: {e}")
    
    logger.info(
        "Tool initialization complete",
        tools_initialized=tools_initialized,
        tools_available=[tool.name for tool in registry.list_tools()]
    )


def get_tool_summary() -> Dict[str, any]:
    """
    Get a summary of all available tools
    
    Returns:
        Dictionary with tool categories and counts
    """
    return {
        "total_tools": 5,
        "categories": {
            "analysis": ["analyze_project", "analyze_code"],
            "prediction": ["predict_risk"],
            "integration": ["jira_integration", "github_integration"]
        },
        "capabilities": {
            "project_management": True,
            "code_analysis": True,
            "risk_prediction": True,
            "jira_integration": True,
            "github_integration": True
        }
    }
