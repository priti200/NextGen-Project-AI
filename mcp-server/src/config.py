"""
Configuration management for MCP Server
"""
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8080
    mcp_log_level: str = "INFO"
    mcp_debug: bool = False
    mcp_workers: int = 4
    
    # CORS Settings
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # LLM API Keys
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Default Model Configuration
    default_model: str = "gemini-pro"
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Database Configuration
    database_url: str = "postgresql+asyncpg://mcp_user:mcp_password@localhost:5432/mcp_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Session Configuration
    session_expire_minutes: int = 60
    max_context_length: int = 10000
    
    # Integration APIs
    jira_api_url: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_email: Optional[str] = None
    
    github_token: Optional[str] = None
    github_api_url: str = "https://api.github.com"
    
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Security
    secret_key: str = "change_this_secret_key_in_production"
    algorithm: str = "HS256"
    
    # Custom Model Configuration (dynamically loaded)
    # Format: CUSTOM_MODEL_<N>_<PROPERTY>
    # These are loaded dynamically in get_custom_models()
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_allowed_origins(self) -> List[str]:
        """Parse comma-separated CORS origins"""
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def validate_model_config(self, model_name: str) -> bool:
        """Validate if model is configured with required API key"""
        if model_name.startswith("gemini"):
            return self.google_api_key is not None
        elif model_name.startswith("gpt"):
            return self.openai_api_key is not None
        elif model_name.startswith("claude"):
            return self.anthropic_api_key is not None
        elif model_name.startswith("custom-"):
            return True  # Custom models are validated separately
        return False
    
    def get_custom_models(self) -> List[Dict[str, Any]]:
        """
        Parse custom model configurations from environment variables
        
        Returns:
            List of custom model configurations
        """
        import os
        custom_models = []
        model_index = 1
        
        while True:
            prefix = f"CUSTOM_MODEL_{model_index}_"
            name_key = f"{prefix}NAME"
            
            # Check if this custom model is configured
            if name_key not in os.environ:
                break
            
            # Extract configuration
            config = {
                "name": os.environ.get(name_key),
                "base_url": os.environ.get(f"{prefix}BASE_URL"),
                "api_key": os.environ.get(f"{prefix}API_KEY", "dummy"),
                "max_tokens": int(os.environ.get(f"{prefix}MAX_TOKENS", "4096")),
                "supports_tools": os.environ.get(f"{prefix}SUPPORTS_TOOLS", "false").lower() == "true",
                "supports_vision": os.environ.get(f"{prefix}SUPPORTS_VISION", "false").lower() == "true",
            }
            
            # Validate required fields
            if config["name"] and config["base_url"]:
                custom_models.append(config)
            
            model_index += 1
        
        return custom_models


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Model configurations
MODEL_CONFIGS = {
    "gemini-pro": {
        "provider": "google",
        "max_tokens": 2048,
        "temperature": 0.7,
        "supports_vision": False,
        "supports_tools": True,
    },
    "gemini-pro-vision": {
        "provider": "google",
        "max_tokens": 2048,
        "temperature": 0.7,
        "supports_vision": True,
        "supports_tools": True,
    },
    "gpt-4": {
        "provider": "openai",
        "max_tokens": 8192,
        "temperature": 0.7,
        "supports_vision": False,
        "supports_tools": True,
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "max_tokens": 128000,
        "temperature": 0.7,
        "supports_vision": True,
        "supports_tools": True,
    },
    "gpt-3.5-turbo": {
        "provider": "openai",
        "max_tokens": 4096,
        "temperature": 0.7,
        "supports_vision": False,
        "supports_tools": True,
    },
    "claude-3-opus": {
        "provider": "anthropic",
        "max_tokens": 4096,
        "temperature": 0.7,
        "supports_vision": True,
        "supports_tools": True,
    },
    "claude-3-sonnet": {
        "provider": "anthropic",
        "max_tokens": 4096,
        "temperature": 0.7,
        "supports_vision": True,
        "supports_tools": True,
    },
}


def get_model_config(model_name: str) -> dict:
    """Get configuration for a specific model"""
    return MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["gemini-pro"])
