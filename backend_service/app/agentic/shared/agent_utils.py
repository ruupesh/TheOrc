"""
Shared utilities for A2A agent bootstrapping.

Provides reusable middleware, conversation-logging callbacks, and a factory
function so that each agent module stays concise and consistent.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.planners import BuiltInPlanner
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.genai import types
from a2a.types import AgentCard, AgentCapabilities, AgentSkill

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from jose import JWTError, jwt

from app.core.config import settings

try:
    from app.utils.logging import logger
except ModuleNotFoundError:
    from utils.logging import logger


# ---------------------------------------------------------------------------
# JWT validation (shared across all A2A agents)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CENTRAL_CONVERSATION_LOGS_DIR = PROJECT_ROOT / "conversation_logs"


def _truncate_value(value: Any, max_length: int = 500) -> Any:
    if isinstance(value, str):
        return value if len(value) <= max_length else f"{value[:max_length]}..."
    return value


def _sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    sanitized = dict(headers)
    auth_header = sanitized.get("authorization")
    if auth_header:
        sanitized["authorization"] = "Bearer ***REDACTED***"
    return sanitized


def _extract_parts(parts) -> list[dict[str, Any]]:
    extracted_parts = []
    for part in parts:
        part_info: dict[str, Any] = {}
        if getattr(part, "text", None):
            part_info["text"] = _truncate_value(part.text)
        if getattr(part, "function_call", None):
            part_info["function_call"] = {
                "name": part.function_call.name,
                "args": _truncate_value(str(getattr(part.function_call, "args", None))),
            }
        if getattr(part, "function_response", None):
            part_info["function_response"] = {
                "name": part.function_response.name,
                "response": _truncate_value(str(part.function_response.response)),
            }
        if part_info:
            extracted_parts.append(part_info)
    return extracted_parts


def _find_latest_event_payload(
    session, *, prefer_author: str | None = None
) -> dict[str, Any] | None:
    for event in reversed(session.events):
        if prefer_author and event.author != prefer_author:
            continue
        if event.content and event.content.parts:
            return {
                "author": event.author,
                "role": event.content.role,
                "parts": _extract_parts(event.content.parts),
            }
    return None


def _get_reasoning_effort() -> str | None:
    return os.getenv("AGENT_REASONING_EFFORT", None)


def _get_thinking_level() -> types.ThinkingLevel | None:
    level = os.getenv("AGENT_THINKING_LEVEL", None)
    return getattr(types.ThinkingLevel, level, types.ThinkingLevel.MEDIUM) if level is not None else types.ThinkingLevel.MEDIUM


def _get_include_thoughts() -> bool:
    return os.getenv("AGENT_INCLUDE_THOUGHTS", "false").lower() == "true"


def build_reasoning_config() -> types.ThinkingConfig:
    return types.ThinkingConfig(
        include_thoughts=_get_include_thoughts(),
        thinking_level=_get_thinking_level(),
    )


def build_agent_model(model: str) -> LiteLlm:
    return LiteLlm(
        model=model,
        reasoning_effort=_get_reasoning_effort(),
    )


def build_builtin_planner() -> BuiltInPlanner:
    return BuiltInPlanner(thinking_config=build_reasoning_config())


def is_a2a_auth_required() -> bool:
    """Return whether remote A2A agent endpoints should enforce JWT auth."""
    return os.getenv("A2A_AUTH_REQUIRED", "false").lower() == "true"


def validate_jwt(token: str) -> bool:
    """Validate a JWT using the same settings as the main API."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload.get("sub") is not None
    except JWTError:
        return False


class JWTValidationMiddleware(BaseHTTPMiddleware):
    """Validate JWT tokens on incoming A2A requests.

    Exempt paths (agent card, health) are allowed without authentication.
    """

    EXEMPT_PATHS = {
        "/.well-known/agent.json",
        "/.well-known/agent-card.json",
        "/health",
    }

    async def dispatch(self, request: Request, call_next):
        if not is_a2a_auth_required():
            return await call_next(request)

        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid Authorization header format. Use 'Bearer <token>'"
                },
            )

        token = auth_header[7:]
        if not validate_jwt(token):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        return await call_next(request)


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming and outgoing HTTP traffic for an A2A agent."""

    def __init__(self, app, agent_name: str):
        super().__init__(app)
        self.agent_name = agent_name

    async def dispatch(self, request: Request, call_next):
        raw_body = await request.body()
        body_preview = _truncate_value(raw_body.decode("utf-8", errors="replace"))
        logger.info(
            "Incoming agent HTTP request",
            agent_name=self.agent_name,
            method=request.method,
            path=request.url.path,
            query=str(request.url.query),
            headers=_sanitize_headers(dict(request.headers)),
            body_preview=body_preview,
        )

        response = await call_next(request)

        logger.info(
            "Outgoing agent HTTP response",
            agent_name=self.agent_name,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            content_type=response.headers.get("content-type"),
        )
        return response


# ---------------------------------------------------------------------------
# Conversation-logging callback factory
# ---------------------------------------------------------------------------


def create_log_callback(agent_name: str):
    """Return a ``before_agent_callback`` that logs conversation history.

    The callback also hydrates ``conversation_history`` from A2A metadata
    so the agent can access the orchestrator's conversation context.
    """

    def log_conversation_history(callback_context: CallbackContext):
        try:
            # Hydrate conversation_history from orchestrator metadata
            run_config = callback_context.run_config
            if run_config and run_config.custom_metadata:
                a2a_meta = run_config.custom_metadata.get("a2a_metadata", {})
                orchestrator_history = a2a_meta.get("conversation_history")
                if orchestrator_history:
                    callback_context.state["conversation_history"] = (
                        orchestrator_history
                    )
                    logger.info(
                        "Received orchestrator conversation_history",
                        len_of_history=len(orchestrator_history),
                    )

            session = callback_context._invocation_context.session
            invocation_id = callback_context._invocation_context.invocation_id
            session_logs_dir = CENTRAL_CONVERSATION_LOGS_DIR / session.id
            session_logs_dir.mkdir(parents=True, exist_ok=True)

            log_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "session_id": session.id,
                "invocation_id": invocation_id,
                "app_name": session.app_name,
                "user_id": session.user_id,
                "last_update": str(session.last_update_time),
                "state": dict(session.state),
                "events": [],
            }

            for event in session.events:
                event_data = {
                    "invocation_id": event.invocation_id,
                    "author": event.author,
                    "content": None,
                    "actions": None,
                }

                if event.content and event.content.parts:
                    event_data["content"] = {"role": event.content.role, "parts": []}
                    for part in event.content.parts:
                        part_info = {}
                        if part.text:
                            part_info["text"] = part.text
                        if part.function_call:
                            part_info["function_call"] = {
                                "name": part.function_call.name,
                                "args": (
                                    part.function_call.args
                                    if hasattr(part.function_call, "args")
                                    else None
                                ),
                            }
                        if part.function_response:
                            part_info["function_response"] = {
                                "name": part.function_response.name,
                                "response": str(part.function_response.response)[:200],
                            }
                        event_data["content"]["parts"].append(part_info)

                if event.actions:
                    event_data["actions"] = {
                        "state_delta": (
                            event.actions.state_delta
                            if event.actions.state_delta
                            else None
                        ),
                        "transfer_to_agent": (
                            event.actions.transfer_to_agent
                            if hasattr(event.actions, "transfer_to_agent")
                            and event.actions.transfer_to_agent
                            else None
                        ),
                    }

                log_data["events"].append(event_data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            log_file = (
                session_logs_dir
                / f"{agent_name}_conversation_{invocation_id}_{timestamp}.json"
            )

            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

            logger.info(
                "Conversation history logged",
                log_file=str(log_file),
                total_events=len(session.events),
            )

        except Exception as e:
            logger.error(f"Error logging conversation history: {e}")

    return log_conversation_history


def create_response_log_callback(agent_name: str):
    """Return an ``after_agent_callback`` that logs the agent's latest output."""

    def log_latest_response(callback_context: CallbackContext):
        try:
            session = callback_context._invocation_context.session
            latest_user_payload = _find_latest_event_payload(
                session, prefer_author="user"
            )
            latest_agent_payload = _find_latest_event_payload(
                session, prefer_author=agent_name
            ) or _find_latest_event_payload(session)

            logger.info(
                "Agent invocation processed",
                agent_name=agent_name,
                session_id=session.id,
                invocation_id=callback_context._invocation_context.invocation_id,
                latest_user_input=latest_user_payload,
                latest_agent_output=latest_agent_payload,
            )
        except Exception as e:
            logger.error(f"Error logging agent response: {e}")

    return log_latest_response


# ---------------------------------------------------------------------------
# A2A agent factory
# ---------------------------------------------------------------------------


def build_a2a_agent(
    *,
    agent_name: str,
    description: str,
    instruction: str,
    tools: list,
    port: int,
    model: str | None = None,
    agent_dir: str | Path | None = None,
):
    """Create an A2A-ready ``Agent`` and Starlette app with standard middleware.

    Args:
        agent_name: Unique name for the agent (used in ``transfer_to_agent``).
        description: Short description visible to the orchestrator.
        instruction: Full system prompt for the agent.
        tools: List of tools / ``McpToolset`` instances.
        port: Port number for the A2A server.
        model: LiteLLM model string.  Defaults to ``AGENT_MODEL`` env var.
        agent_dir: Retained for backward compatibility. Conversation logs are
                   now written to the project-level ``conversation_logs``
                   directory grouped by ``session_id``.

    Returns:
        Tuple of ``(a2a_app, root_agent)``.
    """
    if agent_dir is None:
        agent_dir = Path(__file__).parent.parent / agent_name

    agent_dir = Path(agent_dir)
    root_env_path = PROJECT_ROOT / ".env"
    agent_env_path = agent_dir / ".env"

    load_dotenv(root_env_path)
    load_dotenv(agent_env_path, override=True)

    if model is None:
        model = os.getenv("AGENT_MODEL", "gemini/gemini-2.5-flash")

    log_callback = create_log_callback(agent_name)
    response_log_callback = create_response_log_callback(agent_name)

    root_agent = Agent(
        name=agent_name,
        model=build_agent_model(model),
        description=description,
        instruction=instruction,
        tools=tools,
        before_agent_callback=log_callback,
        after_agent_callback=response_log_callback,
    )
    static_agent_card = AgentCard(
            name=agent_name,
            description=description,
            url=f"http://localhost:{port}/",
            version="1.0.0",
            capabilities=AgentCapabilities(),
            skills=[
                AgentSkill(
                    id=agent_name,
                    name=agent_name.replace("-", " ").title(),
                    description=description,
                    tags=[agent_name],
                )
            ],
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"],
        )
    a2a_app = to_a2a(root_agent, port=port, agent_card=static_agent_card)
    a2a_app.add_middleware(RequestResponseLoggingMiddleware, agent_name=agent_name)
    a2a_app.add_middleware(JWTValidationMiddleware)

    return a2a_app, root_agent
