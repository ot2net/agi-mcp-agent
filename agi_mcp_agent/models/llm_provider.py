"""Database models for LLM providers and model configurations."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LLMProviderModel(Base):
    """Database model for LLM providers."""
    
    __tablename__ = "llm_providers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    is_enabled = Column(Boolean, default=True)
    is_builtin = Column(Boolean, default=False)
    region = Column(String(50), nullable=True)  # e.g. 'global', 'cn', 'us', etc.
    provider_module = Column(String(255), nullable=False)
    provider_class = Column(String(255), nullable=False)
    api_key = Column(Text, nullable=True)  # Make api_key nullable
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    models = relationship("LLMModelModel", back_populates="provider", cascade="all, delete-orphan")
    settings = relationship("LLMProviderSettingModel", back_populates="provider", cascade="all, delete-orphan")


class LLMProviderSettingModel(Base):
    """Database model for LLM provider settings."""
    
    __tablename__ = "llm_provider_settings"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("llm_providers.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    is_secret = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("LLMProviderModel", back_populates="settings")
    
    # Unique constraint across provider_id and key
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class LLMModelModel(Base):
    """Database model for LLM models."""
    
    __tablename__ = "llm_models"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("llm_providers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    model_id = Column(String(200), nullable=False)  # Actual ID used in API calls
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    model_type = Column(String(50), nullable=True)  # chat, completion, embedding, etc.
    is_enabled = Column(Boolean, default=True)
    max_tokens = Column(Integer, nullable=True)
    supports_streaming = Column(Boolean, default=True)
    supports_function_calling = Column(Boolean, default=False)
    context_window = Column(Integer, nullable=True)
    pricing_input = Column(Float, nullable=True)  # per 1K tokens
    pricing_output = Column(Float, nullable=True)  # per 1K tokens
    capabilities = Column(JSON, nullable=True)  # JSON representation of capabilities
    parameters = Column(JSON, nullable=True)  # Default parameters
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship("LLMProviderModel", back_populates="models")
    
    # Unique constraint across provider_id and name
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


def get_default_providers() -> List[Dict[str, Any]]:
    """Get default provider configurations."""
    return [
        {
            "name": "openai",
            "type": "openai",  # Explicitly set type
            "display_name": "OpenAI",
            "description": "OpenAI models including GPT-3.5 and GPT-4",
            "website": "https://openai.com/",
            "is_enabled": True,
            "is_builtin": True,
            "region": "global",
            "provider_module": "agi_mcp_agent.agent.llm_providers.openai",
            "provider_class": "OpenAIProvider",
        },
        {
            "name": "anthropic",
            "type": "anthropic",  # Explicitly set type
            "display_name": "Anthropic",
            "description": "Anthropic Claude models",
            "website": "https://www.anthropic.com/",
            "is_enabled": True,
            "is_builtin": True,
            "region": "global",
            "provider_module": "agi_mcp_agent.agent.llm_providers.anthropic",
            "provider_class": "AnthropicProvider",
        },
        {
            "name": "google",
            "type": "google",  # Explicitly set type
            "display_name": "Google AI",
            "description": "Google Gemini models",
            "website": "https://ai.google.dev/",
            "is_enabled": True,
            "is_builtin": True,
            "region": "global",
            "provider_module": "agi_mcp_agent.agent.llm_providers.google",
            "provider_class": "GoogleProvider",
        },
        {
            "name": "mistral",
            "type": "mistral",  # Explicitly set type
            "display_name": "Mistral AI",
            "description": "Mistral AI models",
            "website": "https://mistral.ai/",
            "is_enabled": True,
            "is_builtin": True,
            "region": "global",
            "provider_module": "agi_mcp_agent.agent.llm_providers.mistral",
            "provider_class": "MistralProvider",
        },
        {
            "name": "qwen",
            "type": "rest",  # Set a default type for providers without dedicated types
            "display_name": "Qwen",
            "description": "Qwen models from Alibaba Cloud",
            "website": "https://qwen.ai/",
            "is_enabled": True,
            "is_builtin": True,
            "region": "global",
            "provider_module": "agi_mcp_agent.agent.llm_providers.qwen",
            "provider_class": "QwenProvider",
        },
        {
            "name": "deepseek",
            "type": "deepseek",  # Updated from 'test' to 'deepseek'
            "display_name": "DeepSeek",
            "description": "DeepSeek AI models",
            "website": "https://deepseek.ai/",
            "is_enabled": True,
            "is_builtin": True,
            "region": "global",
            "provider_module": "agi_mcp_agent.agent.llm_providers.deepseek",
            "provider_class": "DeepSeekProvider",
        }
    ]


def get_default_provider_settings() -> List[Dict[str, Any]]:
    """Get the default provider settings to be inserted in the database."""
    return [
        # OpenAI settings
        {
            "provider_name": "openai",
            "key": "api_key",
            "value": None,
            "is_secret": True,
            "is_required": True,
            "description": "OpenAI API key",
        },
        {
            "provider_name": "openai",
            "key": "organization_id",
            "value": None,
            "is_secret": False,
            "is_required": False,
            "description": "OpenAI organization ID",
        },
        {
            "provider_name": "openai",
            "key": "api_base",
            "value": "https://api.openai.com/v1",
            "is_secret": False,
            "is_required": False,
            "description": "OpenAI API base URL",
        },
        
        # Anthropic settings
        {
            "provider_name": "anthropic",
            "key": "api_key",
            "value": None,
            "is_secret": True,
            "is_required": True,
            "description": "Anthropic API key",
        },
        
        # Google settings
        {
            "provider_name": "google",
            "key": "api_key",
            "value": None,
            "is_secret": True,
            "is_required": True,
            "description": "Google API key",
        },
        {
            "provider_name": "google",
            "key": "project_id",
            "value": None,
            "is_secret": False,
            "is_required": False,
            "description": "Google Cloud project ID",
        },
        
        # Mistral settings
        {
            "provider_name": "mistral",
            "key": "api_key",
            "value": None,
            "is_secret": True,
            "is_required": True,
            "description": "Mistral AI API key",
        },
        
        # DeepSeek settings
        {
            "provider_name": "deepseek",
            "key": "api_key",
            "value": None,
            "is_secret": True,
            "is_required": True,
            "description": "DeepSeek API key",
        },
        {
            "provider_name": "deepseek",
            "key": "api_base",
            "value": "https://api.deepseek.com/v1",
            "is_secret": False,
            "is_required": False,
            "description": "DeepSeek API base URL",
        },
        
        # Qwen settings
        {
            "provider_name": "qwen",
            "key": "api_key",
            "value": None,
            "is_secret": True,
            "is_required": True,
            "description": "Qwen API key",
        },
        {
            "provider_name": "qwen",
            "key": "api_base",
            "value": "https://dashscope.aliyuncs.com/api/v1",
            "is_secret": False,
            "is_required": False,
            "description": "Qwen API base URL (DashScope)",
        },
    ] 