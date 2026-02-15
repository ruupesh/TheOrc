"""
Adapters package — Factories for creating ADK agents and toolsets from YAML configuration.

Provides:
    - ``McpAdapter``          : Builds ``McpToolset`` objects from ``mcp_conf.yml``
    - ``RemoteA2aAdapter``    : Builds ``RemoteA2aAgent`` objects from ``remote_agents_conf.yml``
    - ``get_mcp_conf()``      : Raw YAML parser for MCP configs
    - ``get_remote_a2a_conf()``: Raw YAML parser for remote agent configs
"""

from .mcp_adapter import McpAdapter, get_mcp_conf
from .remote_a2a_adapter import RemoteA2aAdapter, get_remote_a2a_conf

__all__ = [
    "McpAdapter",
    "RemoteA2aAdapter",
    "get_mcp_conf",
    "get_remote_a2a_conf",
]
