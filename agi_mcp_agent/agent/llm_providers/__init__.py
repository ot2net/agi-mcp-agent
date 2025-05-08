"""LLM providers module for AGI-MCP-Agent.

This module provides integrations with various LLM providers like OpenAI, Anthropic, etc.
It abstracts away the differences between different LLM APIs to provide a unified interface.
"""

from agi_mcp_agent.agent.llm_providers.base import LLMProvider, ModelConfig
from agi_mcp_agent.agent.llm_providers.openai import OpenAIProvider

# Add imports for all providers as they are implemented
try:
    from agi_mcp_agent.agent.llm_providers.anthropic import AnthropicProvider
except ImportError:
    pass

try:
    from agi_mcp_agent.agent.llm_providers.huggingface import HuggingFaceProvider
except ImportError:
    pass

try:
    from agi_mcp_agent.agent.llm_providers.llama import LlamaProvider
except ImportError:
    pass

try:
    from agi_mcp_agent.agent.llm_providers.google import GoogleProvider
except ImportError:
    pass

try:
    from agi_mcp_agent.agent.llm_providers.mistral import MistralProvider
except ImportError:
    pass

try:
    from agi_mcp_agent.agent.llm_providers.cohere import CohereProvider
except ImportError:
    pass

__all__ = [
    'LLMProvider',
    'ModelConfig',
    'OpenAIProvider',
    'AnthropicProvider',
    'HuggingFaceProvider',
    'LlamaProvider',
    'GoogleProvider',
    'MistralProvider',
    'CohereProvider',
] 