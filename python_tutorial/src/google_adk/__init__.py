"""
Google Agent Development Kit (ADK) Tutorial Package
"""

from .adk_tutorial import Agent, AgentConfig, Tool, get_weather, search_information, create_sample_agent
from .mcp import (
    create_context,
    list_contexts,
    set_active_context,
    get_active_context,
    set_context_value,
    get_context_value,
    delete_context
)

try:
    from mcp_agent.app import MCPApp
    from mcp_agent.agents.agent import Agent as MCPAgent
    from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
    HAS_MCP_AGENT = True
except ImportError:
    HAS_MCP_AGENT = False
