"""
Model factory and initialization
"""
from typing import Optional
import structlog

from .base import BaseModel, model_registry
from .gemini import GeminiModel
from .openai import OpenAIModel
from .claude import ClaudeModel
from .custom import CustomModel, OllamaModel, LMStudioModel, LocalAIModel
from config import get_settings

logger = structlog.get_logger(__name__)


def initialize_models() -> None:
    """
    Initialize and register all configured LLM models
    
    Only models with valid API keys will be registered
    """
    settings = get_settings()
    
    # Initialize Google Gemini models
    if settings.google_api_key:
        try:
            # Register Gemini Pro
            gemini_pro = GeminiModel(
                api_key=settings.google_api_key,
                model_name="gemini-2.5-pro",
                max_tokens=2048
            )
            model_registry.register("gemini-pro", gemini_pro)
            logger.info("Registered model", model="gemini-pro")
            
            # Register Gemini Pro Vision
            gemini_vision = GeminiModel(
                api_key=settings.google_api_key,
                model_name="gemini-pro-vision",
                max_tokens=2048
            )
            model_registry.register("gemini-pro-vision", gemini_vision)
            logger.info("Registered model", model="gemini-pro-vision")
            
        except Exception as e:
            logger.error("Failed to initialize Gemini models", error=str(e))
    else:
        logger.warning("Gemini API key not configured, skipping Gemini models")
    
    # Initialize OpenAI models
    if settings.openai_api_key:
        try:
            # Register GPT-4
            gpt4 = OpenAIModel(
                api_key=settings.openai_api_key,
                model_name="gpt-4"
            )
            model_registry.register("gpt-4", gpt4)
            logger.info("Registered model", model="gpt-4")
            
            # Register GPT-4 Turbo
            gpt4_turbo = OpenAIModel(
                api_key=settings.openai_api_key,
                model_name="gpt-4-turbo"
            )
            model_registry.register("gpt-4-turbo", gpt4_turbo)
            logger.info("Registered model", model="gpt-4-turbo")
            
            # Register GPT-3.5 Turbo
            gpt35 = OpenAIModel(
                api_key=settings.openai_api_key,
                model_name="gpt-3.5-turbo"
            )
            model_registry.register("gpt-3.5-turbo", gpt35)
            logger.info("Registered model", model="gpt-3.5-turbo")
            
        except Exception as e:
            logger.error("Failed to initialize OpenAI models", error=str(e))
    else:
        logger.warning("OpenAI API key not configured, skipping OpenAI models")
    
    # Initialize Anthropic Claude models
    if settings.anthropic_api_key:
        try:
            # Register Claude 3 Opus
            claude_opus = ClaudeModel(
                api_key=settings.anthropic_api_key,
                model_name="claude-3-opus-20240229"
            )
            model_registry.register("claude-3-opus", claude_opus)
            logger.info("Registered model", model="claude-3-opus")
            
            # Register Claude 3 Sonnet
            claude_sonnet = ClaudeModel(
                api_key=settings.anthropic_api_key,
                model_name="claude-3-sonnet-20240229"
            )
            model_registry.register("claude-3-sonnet", claude_sonnet)
            logger.info("Registered model", model="claude-3-sonnet")
            
            # Register Claude 3 Haiku
            claude_haiku = ClaudeModel(
                api_key=settings.anthropic_api_key,
                model_name="claude-3-haiku-20240307"
            )
            model_registry.register("claude-3-haiku", claude_haiku)
            logger.info("Registered model", model="claude-3-haiku")
            
        except Exception as e:
            logger.error("Failed to initialize Claude models", error=str(e))
    else:
        logger.warning("Anthropic API key not configured, skipping Claude models")
    
    # Initialize custom/open-source models
    custom_models = settings.get_custom_models()
    if custom_models:
        logger.info("Initializing custom models", count=len(custom_models))
        
        for config in custom_models:
            try:
                model_name = config["name"]
                
                # Determine if it's a known local model type
                if "ollama" in config["base_url"].lower():
                    model = OllamaModel(
                        model_name=model_name,
                        base_url=config["base_url"],
                        max_tokens=config["max_tokens"]
                    )
                elif "1234" in config["base_url"]:  # LM Studio default port
                    model = LMStudioModel(
                        model_name=model_name,
                        base_url=config["base_url"],
                        max_tokens=config["max_tokens"],
                        supports_tools=config["supports_tools"],
                        supports_vision=config["supports_vision"]
                    )
                else:
                    # Generic custom model
                    model = CustomModel(
                        api_key=config["api_key"],
                        base_url=config["base_url"],
                        model_name=model_name,
                        max_tokens=config["max_tokens"],
                        supports_tools=config["supports_tools"],
                        supports_vision=config["supports_vision"]
                    )
                
                # Register with custom- prefix to distinguish from official models
                registry_name = f"custom-{model_name}"
                model_registry.register(registry_name, model)
                logger.info("Registered custom model", 
                           model=registry_name, 
                           base_url=config["base_url"])
                
            except Exception as e:
                logger.error("Failed to initialize custom model", 
                           model=config.get("name"),
                           error=str(e))
    else:
        logger.info("No custom models configured")
    
    # Log summary
    registered_models = model_registry.list_models()
    logger.info("Model initialization complete", 
                total_models=len(registered_models),
                models=registered_models)


def get_model(model_name: str) -> Optional[BaseModel]:
    """
    Get a registered model by name
    
    Args:
        model_name: Name of the model to retrieve
        
    Returns:
        Model instance or None if not found
    """
    return model_registry.get(model_name)


def list_available_models() -> list[str]:
    """
    List all available models
    
    Returns:
        List of model names
    """
    return model_registry.list_models()
