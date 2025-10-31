"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "NextGen Project AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/projectai"
    
    # Redis settings (for caching and rate limiting)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Integration APIs
    JIRA_BASE_URL: str = ""
    JIRA_API_TOKEN: str = ""
    JIRA_EMAIL: str = ""
    
    GITHUB_TOKEN: str = ""
    GITHUB_ORG: str = ""
    
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""
    SLACK_WEBHOOK_URL: str = ""
    
    # ML Service settings
    ML_SERVICE_URL: str = "http://localhost:5001"
    RISK_PREDICTION_ENDPOINT: str = "/predict-risk"
    SUMMARIZATION_ENDPOINT: str = "/summarize"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
