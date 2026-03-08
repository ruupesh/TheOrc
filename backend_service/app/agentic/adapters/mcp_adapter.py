"""
MCP Adapter - Factory for creating McpToolset objects from YAML configuration.

Parses `mcp_conf.yml` and produces a list of configured McpToolset instances,
supporting Stdio, StreamableHTTP, and SSE connection types.

Usage:
    adapter = McpAdapter()
    toolsets = adapter.get_mcp_tool_sets()
    # Returns: list[McpToolset]
"""

import os
import shutil
from pathlib import Path
from string import Template
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    SseConnectionParams,
    StreamableHTTPConnectionParams,
)

from app.utils.logging import logger

# Path to the default configuration file (same directory as this module)
_DEFAULT_CONF_PATH = Path(__file__).parent / "mcp_conf.yml"
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_ENV_VALUES = {
    "DDG_MCP_PATH": str(
        _PROJECT_ROOT
        / "venv"
        / "Lib"
        / "site-packages"
        / "duckduckgo_mcp_server"
        / "server.py"
    ),
    "FILESYSTEM_ALLOWED_PATHS": str(_PROJECT_ROOT),
    "SQLITE_DB_PATH": str(_PROJECT_ROOT / "database.db"),
    "GIT_REPO_PATH": str(_PROJECT_ROOT),
    "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", ""),
}


def _substitute_value(value: Any, substitutions: dict[str, str]) -> Any:
    if isinstance(value, str):
        return (
            Template(value).safe_substitute(substitutions) if "${" in value else value
        )
    if isinstance(value, list):
        return [_substitute_value(item, substitutions) for item in value]
    if isinstance(value, dict):
        return {
            key: _substitute_value(item, substitutions) for key, item in value.items()
        }
    return value


class McpToolsetConfig(BaseModel):
    """Validated schema for a single MCP toolset entry in mcp_conf.yml."""

    name: str
    connection_type: str  # "stdio" | "streamable_http" | "sse"

    # Stdio-specific
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    env: Optional[dict[str, str]] = None

    # HTTP/SSE-specific
    url: Optional[str] = None
    headers: Optional[dict[str, str]] = None
    sse_read_timeout: float = 300.0

    # Common
    timeout: float = 30.0
    authentication_flag: bool = False
    auth_token: Optional[str] = None
    tool_filter: Optional[list[str]] = None


def get_mcp_conf(config_path: Optional[str | Path] = None) -> list[dict[str, Any]]:
    """Parse `mcp_conf.yml` and return the raw list of toolset configurations.

    Performs environment-variable substitution on string values using
    ``${VAR_NAME}`` syntax so that secrets/paths are not hardcoded.

    Args:
        config_path: Absolute or relative path to the YAML file.
                     Defaults to ``mcp_conf.yml`` in the adapters directory.

    Returns:
        A list of dictionaries, one per toolset entry.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the file is empty or missing the ``mcp_toolsets`` key.
    """
    path = Path(config_path) if config_path else _DEFAULT_CONF_PATH

    if not path.exists():
        raise FileNotFoundError(f"MCP config file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not raw or "mcp_toolsets" not in raw:
        raise ValueError(
            f"Invalid MCP config — expected top-level 'mcp_toolsets' key in {path}"
        )

    configs: list[dict[str, Any]] = raw["mcp_toolsets"]
    substitutions = {**_DEFAULT_ENV_VALUES, **os.environ}

    # Substitute ${ENV_VAR} references with actual environment values
    for cfg in configs:
        for key, value in cfg.items():
            cfg[key] = _substitute_value(value, substitutions)

    return configs


class McpAdapter:
    """Factory that reads MCP configuration and produces ``McpToolset`` instances.

    Args:
        config_path: Path to ``mcp_conf.yml``.  Defaults to the file shipped
                     alongside this module.

    Example::

        adapter = McpAdapter()
        toolsets = adapter.get_mcp_tool_sets()

        # Use individual toolsets in an agent
        agent = Agent(..., tools=toolsets)
    """

    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        auth_token: Optional[str] = None,
        tool_configs_override: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        self._config_path = config_path
        self._auth_token = auth_token
        # Use DB-provided configs if available, otherwise read from YAML
        if tool_configs_override is not None:
            self._raw_configs = tool_configs_override
        else:
            self._raw_configs = get_mcp_conf(self._config_path)
        self._configs: list[McpToolsetConfig] = [
            McpToolsetConfig(**cfg) for cfg in self._raw_configs
        ]

    def get_mcp_tool_sets(self) -> list[McpToolset]:
        """Build and return a list of ``McpToolset`` objects from configuration.

        Each entry in ``mcp_conf.yml`` is converted to a properly parameterised
        ``McpToolset`` with the correct connection type.

        Returns:
            A list of ready-to-use ``McpToolset`` instances.

        Raises:
            ValueError: If an unsupported ``connection_type`` is encountered or
                        required fields are missing for the chosen type.
        """
        toolsets: list[McpToolset] = []
        logger.info(
            "Creating MCP toolset from configuration", configuration=self._configs
        )
        for cfg in self._configs:
            skip_reason = self._get_skip_reason(cfg)
            if skip_reason:
                logger.warning(
                    "Skipping MCP toolset",
                    name=cfg.name,
                    connection_type=cfg.connection_type,
                    reason=skip_reason,
                )
                continue

            try:
                connection_params = self._build_connection_params(cfg)
                toolset = McpToolset(
                    connection_params=connection_params,
                    tool_filter=cfg.tool_filter,
                )
                logger.info(
                    "Created McpToolset",
                    name=cfg.name,
                    connection_type=cfg.connection_type,
                )
                toolsets.append(toolset)
            except Exception as exc:
                logger.warning(
                    "Skipping MCP toolset due to configuration error",
                    name=cfg.name,
                    connection_type=cfg.connection_type,
                    error=str(exc),
                )

        return toolsets

    def get_mcp_tool_set(self, name: str) -> McpToolset:
        """Return a single ``McpToolset`` by its configured name.

        Args:
            name: The ``name`` field from the YAML entry.

        Returns:
            The matching ``McpToolset`` instance.

        Raises:
            KeyError: If no entry with the given name exists.
        """
        for cfg in self._configs:
            if cfg.name == name:
                connection_params = self._build_connection_params(cfg)
                return McpToolset(
                    connection_params=connection_params,
                    tool_filter=cfg.tool_filter,
                )
        raise KeyError(f"No MCP toolset config found with name '{name}'")

    def get_mcp_tool_sets_by_name(self) -> dict[str, McpToolset]:
        """Build and return MCP toolsets indexed by their configuration name.

        Only returns toolsets that pass validation checks.  Toolsets with
        missing commands, unresolved environment variables, or other issues
        are silently skipped (with a warning log).

        Returns:
            A dict mapping toolset name to the ready-to-use ``McpToolset``.
        """
        result: dict[str, McpToolset] = {}

        for cfg in self._configs:
            skip_reason = self._get_skip_reason(cfg)
            if skip_reason:
                logger.warning(
                    "Skipping MCP toolset",
                    name=cfg.name,
                    connection_type=cfg.connection_type,
                    reason=skip_reason,
                )
                continue
            try:
                connection_params = self._build_connection_params(cfg)
                toolset = McpToolset(
                    connection_params=connection_params,
                    tool_filter=cfg.tool_filter,
                )
                logger.info(
                    "Created McpToolset (by-name)",
                    name=cfg.name,
                    connection_type=cfg.connection_type,
                )
                result[cfg.name] = toolset
            except Exception as exc:
                logger.warning(
                    "Skipping MCP toolset due to configuration error",
                    name=cfg.name,
                    connection_type=cfg.connection_type,
                    error=str(exc),
                )

        return result

    @property
    def configs(self) -> list[McpToolsetConfig]:
        """Return the parsed configuration objects (read-only)."""
        return list(self._configs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_connection_params(
        self, cfg: McpToolsetConfig
    ) -> StdioConnectionParams | StreamableHTTPConnectionParams | SseConnectionParams:
        """Convert a validated config into the appropriate ADK connection params.

        Args:
            cfg: A single validated toolset configuration.

        Returns:
            An ADK-compatible connection params object.

        Raises:
            ValueError: On unsupported type or missing required fields.
        """
        if cfg.connection_type == "stdio":
            return self._build_stdio_params(cfg)
        elif cfg.connection_type == "streamable_http":
            return self._build_streamable_http_params(cfg)
        elif cfg.connection_type == "sse":
            return self._build_sse_params(cfg)
        else:
            raise ValueError(
                f"Unsupported connection_type '{cfg.connection_type}' for toolset '{cfg.name}'. "
                "Supported types: stdio, streamable_http, sse"
            )

    def _build_stdio_params(self, cfg: McpToolsetConfig) -> StdioConnectionParams:
        """Build ``StdioConnectionParams`` from config."""
        if not cfg.command:
            raise ValueError(f"'command' is required for stdio toolset '{cfg.name}'")

        args = list(cfg.args)
        if cfg.name == "filesystem" and len(args) > 2:
            normalized_args = args[:2]
            for item in args[2:]:
                if isinstance(item, str) and "," in item:
                    normalized_args.extend(
                        [part.strip() for part in item.split(",") if part.strip()]
                    )
                else:
                    normalized_args.append(item)
            args = normalized_args

        return StdioConnectionParams(
            server_params=StdioServerParameters(
                command=cfg.command,
                args=args,
                env=cfg.env,
            ),
            timeout=cfg.timeout,
        )

    def _get_skip_reason(self, cfg: McpToolsetConfig) -> Optional[str]:
        if cfg.connection_type != "stdio":
            return None

        if not cfg.command:
            return "missing command"

        if shutil.which(cfg.command) is None:
            return f"command '{cfg.command}' is not available"

        unresolved_args = [
            arg for arg in cfg.args if isinstance(arg, str) and "${" in arg
        ]
        if unresolved_args:
            return f"unresolved placeholders in args: {unresolved_args}"

        if cfg.env:
            unresolved_env = {
                key: value
                for key, value in cfg.env.items()
                if isinstance(value, str) and "${" in value
            }
            if unresolved_env:
                return f"unresolved placeholders in env: {unresolved_env}"

        if cfg.name == "github":
            token = (cfg.env or {}).get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
            if not token:
                return "missing GITHUB_PERSONAL_ACCESS_TOKEN"

        if cfg.name == "duckduckgo_search":
            ddg_script = next(
                (
                    arg
                    for arg in cfg.args
                    if isinstance(arg, str) and arg.endswith("server.py")
                ),
                None,
            )
            if not ddg_script or not Path(ddg_script).exists():
                return f"DuckDuckGo MCP server not found at '{ddg_script}'"

        return None

    def _build_streamable_http_params(
        self, cfg: McpToolsetConfig
    ) -> StreamableHTTPConnectionParams:
        """Build ``StreamableHTTPConnectionParams`` from config."""
        if not cfg.url:
            raise ValueError(
                f"'url' is required for streamable_http toolset '{cfg.name}'"
            )
        headers = dict(cfg.headers) if cfg.headers else {}

        # Inject auth header when authentication is enabled
        if cfg.authentication_flag:
            if not self._auth_token:
                raise ValueError(
                    "Authentication flag is set but no auth token was provided"
                )
            headers["Authorization"] = f"Bearer {self._auth_token}"

        return StreamableHTTPConnectionParams(
            url=cfg.url,
            headers=headers if headers else None,
            timeout=cfg.timeout,
            sse_read_timeout=cfg.sse_read_timeout,
        )

    def _build_sse_params(self, cfg: McpToolsetConfig) -> SseConnectionParams:
        """Build ``SseConnectionParams`` from config."""
        if not cfg.url:
            raise ValueError(f"'url' is required for sse toolset '{cfg.name}'")
        headers = dict(cfg.headers) if cfg.headers else {}

        # Inject auth header when authentication is enabled
        if cfg.authentication_flag:
            if not self._auth_token:
                raise ValueError(
                    "Authentication flag is set but no auth token was provided"
                )
            headers["Authorization"] = f"Bearer {self._auth_token}"

        return SseConnectionParams(
            url=cfg.url,
            headers=headers if headers else None,
            timeout=cfg.timeout,
            sse_read_timeout=cfg.sse_read_timeout,
        )
