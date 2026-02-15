"""
Remote A2A Adapter - Factory for creating RemoteA2aAgent objects from YAML configuration.

Parses ``remote_agents_conf.yml`` and produces a list of configured
``RemoteA2aAgent`` instances ready to be used as sub-agents.

Usage:
    adapter = RemoteA2aAdapter()
    agents = adapter.get_remote_agents()
    # Returns: list[RemoteA2aAgent]
"""

import os
import logging
from pathlib import Path
from string import Template
from typing import Any, Optional

import yaml
import httpx
from pydantic import BaseModel, Field
from a2a.client import ClientConfig, ClientFactory

from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

logger = logging.getLogger("google_adk.adapters.remote_a2a_adapter")

# Path to the default configuration file (same directory as this module)
_DEFAULT_CONF_PATH = Path(__file__).parent / "remote_agents_conf.yml"


class RemoteAgentConfig(BaseModel):
    """Validated schema for a single remote agent entry in remote_agents_conf.yml."""

    name: str
    description: str
    host: str
    port: int
    agent_card_path: str = AGENT_CARD_WELL_KNOWN_PATH
    timeout: float = 300.0
    full_history: bool = True
    authentication_flag: bool = False

    @property
    def agent_card_url(self) -> str:
        """Build the full agent-card URL from host, port, and path."""
        base = f"{self.host.rstrip('/')}:{self.port}"
        return f"{base}{self.agent_card_path}"


def get_remote_a2a_conf(
    config_path: Optional[str | Path] = None,
) -> list[dict[str, Any]]:
    """Parse ``remote_agents_conf.yml`` and return the raw list of agent configurations.

    Performs environment-variable substitution on string values using
    ``${VAR_NAME}`` syntax so that secrets/hosts are not hardcoded.

    Args:
        config_path: Absolute or relative path to the YAML file.
                     Defaults to ``remote_agents_conf.yml`` in the adapters directory.

    Returns:
        A list of dictionaries, one per remote agent entry.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the file is empty or missing the ``remote_agents`` key.
    """
    path = Path(config_path) if config_path else _DEFAULT_CONF_PATH

    if not path.exists():
        raise FileNotFoundError(f"Remote agents config file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not raw or "remote_agents" not in raw:
        raise ValueError(
            f"Invalid remote agents config — expected top-level 'remote_agents' key in {path}"
        )

    configs: list[dict[str, Any]] = raw["remote_agents"]

    # Substitute ${ENV_VAR} references with actual environment values
    for cfg in configs:
        for key, value in cfg.items():
            if isinstance(value, str) and "${" in value:
                cfg[key] = Template(value).safe_substitute(os.environ)

    return configs


class RemoteA2aAdapter:
    """Factory that reads remote-agent configuration and produces ``RemoteA2aAgent`` instances.

    Args:
        config_path: Path to ``remote_agents_conf.yml``.  Defaults to the file
                     shipped alongside this module.

    Example::

        adapter = RemoteA2aAdapter()
        agents  = adapter.get_remote_agents()

        root_agent = Agent(
            name="orchestrator",
            sub_agents=agents,
            ...
        )
    """

    def __init__(self, config_path: Optional[str | Path] = None, auth_token: Optional[str] = None) -> None:
        self._config_path = config_path
        self._auth_token = auth_token
        self._raw_configs: list[dict[str, Any]] = get_remote_a2a_conf(self._config_path)
        self._configs: list[RemoteAgentConfig] = [
            RemoteAgentConfig(**cfg) for cfg in self._raw_configs
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_remote_agents(self) -> list[RemoteA2aAgent]:
        """Build and return a list of ``RemoteA2aAgent`` objects from configuration.

        Each entry in ``remote_agents_conf.yml`` is converted to a fully
        configured ``RemoteA2aAgent`` with its own ``ClientFactory`` and
        optional authentication headers.

        Returns:
            A list of ready-to-use ``RemoteA2aAgent`` instances.
        """
        agents: list[RemoteA2aAgent] = []

        for cfg in self._configs:
            agent = self._build_remote_agent(cfg)
            logger.info(
                "Created RemoteA2aAgent '%s' -> %s (auth=%s)",
                cfg.name,
                cfg.agent_card_url,
                cfg.authentication_flag,
            )
            agents.append(agent)

        return agents

    def get_remote_agent(self, name: str) -> RemoteA2aAgent:
        """Return a single ``RemoteA2aAgent`` by its configured name.

        Args:
            name: The ``name`` field from the YAML entry.

        Returns:
            The matching ``RemoteA2aAgent`` instance.

        Raises:
            KeyError: If no entry with the given name exists.
        """
        for cfg in self._configs:
            if cfg.name == name:
                return self._build_remote_agent(cfg)
        raise KeyError(f"No remote agent config found with name '{name}'")

    @property
    def configs(self) -> list[RemoteAgentConfig]:
        """Return the parsed configuration objects (read-only)."""
        return list(self._configs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_remote_agent(self, cfg: RemoteAgentConfig) -> RemoteA2aAgent:
        """Construct a ``RemoteA2aAgent`` from a validated config entry.

        Builds the ``ClientFactory`` with optional authentication headers
        and creates the agent pointing at the correct agent-card URL.

        Args:
            cfg: A single validated remote agent configuration.

        Returns:
            A configured ``RemoteA2aAgent`` instance.
        """
        client_factory = self._build_client_factory(cfg)

        return RemoteA2aAgent(
            name=cfg.name,
            description=cfg.description,
            agent_card=cfg.agent_card_url,
            a2a_client_factory=client_factory,
            full_history_when_stateless=cfg.full_history,
        )

    def _build_client_factory(self, cfg: RemoteAgentConfig) -> ClientFactory:
        """Build an A2A ``ClientFactory`` with optional auth headers.

        When ``authentication_flag`` is ``True`` and ``auth_token`` is provided,
        the underlying ``httpx.AsyncClient`` is created with a pre-configured
        ``Authorization: Bearer <token>`` header.

        Args:
            cfg: A single validated remote agent configuration.

        Returns:
            An ``a2a.client.ClientFactory`` instance.
        """
        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }

        if cfg.authentication_flag:
            if not self._auth_token:
                raise ValueError("Authentication flag is set but no auth token was provided")
            headers["Authorization"] = f"Bearer {self._auth_token}"

        client_config = ClientConfig(
            use_client_preference=True,
            httpx_client=httpx.AsyncClient(
                headers=headers,
                timeout=cfg.timeout,
            ),
        )

        return ClientFactory(client_config)
