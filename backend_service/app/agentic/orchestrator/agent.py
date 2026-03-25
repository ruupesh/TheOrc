import json
import os
from pathlib import Path
from typing import Any
from typing import Optional
from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.apps import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.agents.callback_context import CallbackContext

from app.agentic.prompts_library.orchestrator_agent import SYSTEM_PROMPT
from app.agentic.prompts_library.discovery_agent import build_discovery_prompt
from app.agentic.tools.custom_tools import check_prime, check_weather, find_file_path
from app.agentic.adapters.mcp_adapter import McpAdapter
from app.agentic.adapters.remote_a2a_adapter import RemoteA2aAdapter, RemoteAgentConfig
from app.agentic.shared.agent_utils import build_agent_model, build_builtin_planner
from app.models.schemas.chat import ChatRequest
from app.utils.logging import logger

from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV_PATH)

AGENT_MODEL = os.getenv("AGENT_MODEL")
DEFAULT_AGENT_MODEL = "gemini/gemini-2.5-flash"
ENABLE_DIRECT_MCP_TOOLS = (
    os.getenv("ORCHESTRATOR_ENABLE_DIRECT_MCP_TOOLS", "false").lower() == "true"
)


def _parse_discovery_json(raw: str) -> dict:
    """Parse JSON from discovery agent output, handling markdown code fences."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # remove closing fence
        text = "\n".join(lines)
    return json.loads(text)


approval_find_file_path = FunctionTool(func=find_file_path, require_confirmation=True)
approval_check_prime = FunctionTool(func=check_prime, require_confirmation=True)


def _truncate_value(value: Any, max_length: int = 500) -> Any:
    if isinstance(value, str):
        return value if len(value) <= max_length else f"{value[:max_length]}..."
    return value


class RootAgent:

    def __init__(
        self,
        auth_token: Optional[str] = None,
        request: Optional[ChatRequest] = None,
        db_agent_configs: Optional[list[dict]] = None,
        db_mcp_tool_configs: Optional[list[dict]] = None,
    ) -> None:
        self._auth_token = auth_token
        self._request = request
        self._db_agent_override_supplied = db_agent_configs is not None
        self._db_mcp_override_supplied = db_mcp_tool_configs is not None

        # Build remote agents from DB configs if provided, otherwise from YAML
        if db_agent_configs is not None:
            self.remote_a2a_adapter = RemoteA2aAdapter(
                auth_token=self._auth_token,
                agent_configs_override=db_agent_configs,
            )
        else:
            self.remote_a2a_adapter = RemoteA2aAdapter(auth_token=self._auth_token)

        # Build MCP toolsets from DB configs if provided, otherwise from YAML
        if db_mcp_tool_configs is not None:
            self.mcp_adapter = McpAdapter(
                auth_token=self._auth_token,
                tool_configs_override=db_mcp_tool_configs,
            )
        else:
            self.mcp_adapter = McpAdapter(auth_token=self._auth_token)

        # Pre-build all available remote agents as a name → agent lookup
        self._all_remote_agents: dict[str, Any] = {
            agent.name: agent for agent in self.remote_a2a_adapter.get_remote_agents()
        }

        # Pre-build available MCP toolsets as a name → toolset lookup.
        # If explicit DB configs are provided (including []), honor them
        # regardless of global defaults so per-chat user selection is respected.
        if db_mcp_tool_configs is not None:
            self._all_mcp_toolsets = self.mcp_adapter.get_mcp_tool_sets_by_name()
        else:
            self._all_mcp_toolsets = (
                self.mcp_adapter.get_mcp_tool_sets_by_name()
                if ENABLE_DIRECT_MCP_TOOLS
                else {}
            )

        self.root_agent = self.get_root_agent()

    def update_request_message(self, callback_context: CallbackContext):
        """Append the user's request to conversation_history in session state.

        Runs as before_agent_callback. Uses reassignment (not in-place append)
        so the State object correctly tracks the delta for persistence.
        """
        history = list(callback_context.state.get("conversation_history", []))
        if self._request and self._request.content.message:
            history.append(
                {
                    "role": "user",
                    "content": self._request.content.message,
                }
            )
        elif self._request and self._request.content.hitl_approval:
            history.append(
                {
                    "role": "user",
                    "content": f"[HITL Approval: {[item.model_dump() for item in self._request.content.hitl_approval]}]",
                }
            )
        callback_context.state["conversation_history"] = history
        logger.info(
            "Supervisor received request",
            session_id=callback_context._invocation_context.session.id,
            invocation_id=callback_context._invocation_context.invocation_id,
            message=(
                _truncate_value(self._request.content.message)
                if self._request and self._request.content.message
                else None
            ),
            hitl_approval=(
                [item.model_dump() for item in self._request.content.hitl_approval]
                if self._request and self._request.content.hitl_approval
                else None
            ),
        )

    def update_response_message(self, callback_context: CallbackContext):
        """Append the agent's response to conversation_history in session state.

        Runs as after_agent_callback. By this point the agent has already
        produced its response events, which are available in
        callback_context.session.events. We walk events in reverse to find
        the most recent agent response (text or HITL request) and persist it.
        """
        response_text = None
        hitl_requested = []

        for event in reversed(callback_context.session.events):
            # Skip user-authored events entirely
            if event.author == "user":
                continue
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text = part.text
                    if (
                        hasattr(part, "function_call")
                        and part.function_call
                        and hasattr(part.function_call, "args")
                        and part.function_call.args
                        and "originalFunctionCall" in part.function_call.args
                    ):
                        hitl_requested.append(
                            {
                                "function_id": part.function_call.id,
                                "function_name": part.function_call.name,
                                "confirmed": part.function_call.args.get(
                                    "toolConfirmation", {}
                                ).get("confirmed", False),
                                "payload": part.function_call.args.get(
                                    "originalFunctionCall", {}
                                ).get("args"),
                                "hint": part.function_call.args.get(
                                    "toolConfirmation", {}
                                ).get("hint"),
                            }
                        )
                if response_text or hitl_requested:
                    break

        history = list(callback_context.state.get("conversation_history", []))
        if hitl_requested:
            history.append(
                {
                    "role": "assistant",
                    "content": None,
                    "hitl_requested": hitl_requested,
                }
            )
            callback_context.state["conversation_history"] = history
            logger.info(
                "Supervisor sent HITL request",
                session_id=callback_context._invocation_context.session.id,
                invocation_id=callback_context._invocation_context.invocation_id,
                hitl_requested=hitl_requested,
            )
        elif response_text:
            history.append(
                {
                    "role": "assistant",
                    "content": response_text,
                }
            )
            callback_context.state["conversation_history"] = history
            logger.info(
                "Supervisor sent response",
                session_id=callback_context._invocation_context.session.id,
                invocation_id=callback_context._invocation_context.invocation_id,
                response_text=_truncate_value(response_text),
            )

    # ------------------------------------------------------------------
    # Discovery agent
    # ------------------------------------------------------------------

    def _build_discovery_agent(self) -> Agent:
        """Build the tool/agent discovery agent.

        This agent analyzes the user query and outputs a JSON routing
        decision stored in ``session.state["discovery_result"]`` via
        ``output_key``.
        """
        agent_catalog = (
            "\n".join(
                f"- **{name}**: {agent.description}"
                for name, agent in self._all_remote_agents.items()
            )
            or "No remote agents currently available."
        )

        mcp_catalog = (
            "\n".join(f"- **{name}**" for name in self._all_mcp_toolsets)
            if self._all_mcp_toolsets
            else "No MCP tools currently available."
        )

        return Agent(
            name="tool_agent_discovery",
            model=build_agent_model(AGENT_MODEL or DEFAULT_AGENT_MODEL),
            instruction=build_discovery_prompt(agent_catalog, mcp_catalog),
            output_key="discovery_result",
        )

    # ------------------------------------------------------------------
    # Orchestrator agent (dynamically configured)
    # ------------------------------------------------------------------

    def _configure_orchestrator(self, callback_context: CallbackContext):
        """``before_agent_callback`` for the orchestrator.

        Reads ``discovery_result`` from session state (written by the
        discovery agent) and dynamically sets ``sub_agents`` / ``tools``
        on the orchestrator agent.

        Routing logic:
        * ``single_agent``                   → agent as ``sub_agent``
        * ``multi_agent``                    → agents wrapped in ``AgentTool``
        * ``mcp_tools_only``                 → MCP toolsets only
        * ``mcp_tools_with_single_agent``    → MCP toolsets + agent as ``sub_agent``
        * ``mcp_tools_with_multi_agent``     → MCP toolsets + agents as ``AgentTool``
        """
        raw = callback_context.state.get("discovery_result", "")

        try:
            discovery = _parse_discovery_json(str(raw))
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.warning(
                "Failed to parse discovery result — falling back to all agents as sub_agents",
                raw=_truncate_value(str(raw)),
            )
            self._orchestrator_agent.sub_agents = list(self._all_remote_agents.values())
            self._orchestrator_agent.tools = [
                approval_check_prime,
                check_weather,
                approval_find_file_path,
            ]
            return

        strategy = discovery.get("strategy", "single_agent")
        agent_names = discovery.get("agents", [])
        mcp_tool_names = discovery.get("mcp_tools", [])

        logger.info(
            "Discovery result parsed",
            strategy=strategy,
            agents=agent_names,
            mcp_tools=mcp_tool_names,
            reasoning=discovery.get("reasoning"),
        )

        # Always-available built-in tools
        tools_list = [approval_check_prime, check_weather, approval_find_file_path]
        sub_agents_list = []

        # Add requested MCP tools
        for name in mcp_tool_names:
            if name in self._all_mcp_toolsets:
                tools_list.append(self._all_mcp_toolsets[name])
            else:
                logger.warning("Requested MCP tool not available", name=name)

        # Configure agents based on strategy
        if strategy in ("single_agent", "mcp_tools_with_single_agent"):
            # Single agent → sub_agent (efficient one-hop transfer)
            for name in agent_names:
                if name in self._all_remote_agents:
                    sub_agents_list.append(self._all_remote_agents[name])
                else:
                    logger.warning("Requested agent not available", name=name)
        elif strategy in ("multi_agent", "mcp_tools_with_multi_agent"):
            # Multiple agents → AgentTool (call-and-return for chaining)
            for name in agent_names:
                if name in self._all_remote_agents:
                    tools_list.append(AgentTool(agent=self._all_remote_agents[name]))
                else:
                    logger.warning("Requested agent not available", name=name)
        elif strategy == "mcp_tools_only":
            pass  # Only MCP tools, no agents
        else:
            # Unknown strategy — fall back to sub_agents
            logger.warning(
                "Unknown strategy, falling back to sub_agents", strategy=strategy
            )
            for name in agent_names:
                if name in self._all_remote_agents:
                    sub_agents_list.append(self._all_remote_agents[name])

        self._orchestrator_agent.sub_agents = sub_agents_list
        self._orchestrator_agent.tools = tools_list

        logger.info(
            "Orchestrator dynamically configured",
            strategy=strategy,
            num_sub_agents=len(sub_agents_list),
            sub_agents=[a.name for a in sub_agents_list],
            num_tools=len(tools_list),
        )

    def _build_orchestrator_agent(self) -> Agent:
        """Build the orchestrator agent (tools/sub_agents set dynamically)."""
        return Agent(
            name="Orchestrator",
            model=build_agent_model(AGENT_MODEL or DEFAULT_AGENT_MODEL),
            planner=build_builtin_planner(),
            description="The main orchestrator that executes tasks using dynamically discovered tools and agents.",
            instruction=SYSTEM_PROMPT,
            before_agent_callback=[self._configure_orchestrator],
        )

    # ------------------------------------------------------------------
    # Root sequential agent
    # ------------------------------------------------------------------

    def get_root_agent(self):
        """Build the root ``SequentialAgent``: discovery → orchestrator."""
        logger.info("Building root sequential agent (discovery → orchestrator)...")

        discovery_agent = self._build_discovery_agent()
        self._orchestrator_agent = self._build_orchestrator_agent()

        root_agent = SequentialAgent(
            name="Supervisor",
            sub_agents=[discovery_agent, self._orchestrator_agent],
            before_agent_callback=[self.update_request_message],
            after_agent_callback=[self.update_response_message],
        )

        logger.info(
            "Root sequential agent built",
            discovery_agent=discovery_agent.name,
            orchestrator_agent=self._orchestrator_agent.name,
            num_available_agents=len(self._all_remote_agents),
            available_agents=list(self._all_remote_agents.keys()),
            num_available_mcp_tools=len(self._all_mcp_toolsets),
            available_mcp_tools=list(self._all_mcp_toolsets.keys()),
            direct_mcp_env_enabled=ENABLE_DIRECT_MCP_TOOLS,
            db_agent_override_supplied=self._db_agent_override_supplied,
            db_mcp_override_supplied=self._db_mcp_override_supplied,
        )

        return root_agent

    def get_root_app(self):
        logger.info("Building root app with updated agents and tools...")
        app = App(
            name="Supervisor",
            root_agent=self.root_agent,
            resumability_config=ResumabilityConfig(is_resumable=True),
        )
        return app
