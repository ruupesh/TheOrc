"""Chat API route — user-facing orchestrator endpoint with session ownership and DB-driven agents."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat_message
from app.services.session_service import session_service
from app.services.auth_service import get_or_create_user_session, validate_session_ownership
from app.services.agent_service import get_user_agents
from app.services.mcp_tool_service import get_user_mcp_tools
from app.utils.logging import logger

router = APIRouter()


def _extract_uuid_filter(metadata: dict | None, key: str) -> set[uuid.UUID] | None:
    """Extract a UUID allowlist from request metadata.

    Returns None when the key is absent (meaning no filtering for that key).
    Returns an empty set when the key is present with an empty list
    (meaning explicitly disable all items for that key).
    """
    if not metadata or key not in metadata:
        return None

    raw_values = metadata.get(key)
    if raw_values is None:
        return None
    if not isinstance(raw_values, list):
        logger.warning(
            "Ignoring invalid metadata filter type",
            key=key,
            value_type=type(raw_values).__name__,
        )
        return None

    values: set[uuid.UUID] = set()
    for raw in raw_values:
        if not isinstance(raw, str):
            continue
        try:
            values.add(uuid.UUID(raw))
        except ValueError:
            logger.warning("Ignoring invalid UUID in metadata filter", key=key, value=raw)

    return values


def _agent_to_config(agent) -> dict:
    """Convert an Agent ORM model to a config dict for the adapter."""
    return {
        "name": agent.name,
        "description": agent.description,
        "host": agent.host,
        "port": agent.port,
        "agent_card_path": agent.agent_card_path,
        "timeout": agent.timeout,
        "full_history": agent.full_history,
        "authentication_flag": agent.authentication_flag,
        "allow_conversation_history": agent.allow_conversation_history,
    }


def _mcp_tool_to_config(tool) -> dict:
    """Convert a McpTool ORM model to a config dict for the adapter."""
    cfg = {
        "name": tool.name,
        "connection_type": tool.connection_type,
        "timeout": tool.timeout,
        "authentication_flag": tool.authentication_flag,
    }
    if tool.command:
        cfg["command"] = tool.command
    if tool.args:
        cfg["args"] = tool.args
    if tool.env:
        cfg["env"] = tool.env
    if tool.url:
        cfg["url"] = tool.url
    if tool.headers:
        cfg["headers"] = tool.headers
    if tool.sse_read_timeout:
        cfg["sse_read_timeout"] = tool.sse_read_timeout
    if tool.auth_token:
        cfg["auth_token"] = tool.auth_token
    if tool.tool_filter:
        cfg["tool_filter"] = tool.tool_filter
    return cfg


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Conversation endpoint.

    Receives a user message, processes it through the orchestrator, and returns
    an assistant response. Requires a Bearer JWT token.
    User ID is extracted from JWT — not from the request body.
    Session ownership is enforced: a user can only access their own sessions.
    The orchestrator dynamically loads the user's agents (own + installed) from DB.
    """
    try:
        # Override user_id from JWT (not client-supplied)
        user_id = current_user["user_id"]
        request.user_id = user_id
        session_id = request.session_id

        # Validate / create session ownership record
        user_id_uuid = uuid.UUID(user_id)
        await get_or_create_user_session(db, user_id_uuid, session_id)

        # Load user's agents and MCP tools from DB
        user_agents = await get_user_agents(db, user_id_uuid, include_installed=True)
        user_mcp_tools = await get_user_mcp_tools(db, user_id_uuid)

        metadata = request.content.metadata if isinstance(request.content.metadata, dict) else {}
        enabled_agent_ids = _extract_uuid_filter(metadata, "enabled_agent_ids")
        enabled_mcp_tool_ids = _extract_uuid_filter(metadata, "enabled_mcp_tool_ids")

        if enabled_agent_ids is not None:
            user_agents = [a for a in user_agents if a.id in enabled_agent_ids]
        if enabled_mcp_tool_ids is not None:
            user_mcp_tools = [t for t in user_mcp_tools if t.id in enabled_mcp_tool_ids]

        # Convert to config dicts for adapters.
        # IMPORTANT: keep explicit empty selections as [] (not None), otherwise
        # downstream code interprets None as "use YAML defaults" and disabled
        # items can be unintentionally re-enabled.
        agent_configs = [_agent_to_config(a) for a in user_agents]
        mcp_tool_configs = [_mcp_tool_to_config(t) for t in user_mcp_tools]

        logger.info(
            "Resolved chat capability filters",
            total_agents=len(user_agents),
            total_mcp_tools=len(user_mcp_tools),
            has_agent_filter=enabled_agent_ids is not None,
            has_mcp_filter=enabled_mcp_tool_ids is not None,
        )

        session = await session_service.get_session(
            app_name="orchestrator_api", user_id=user_id, session_id=session_id
        )
        logger.info("Session retrieved", session_id=session_id)
        if not session:
            # Create ADK session
            session = await session_service.create_session(
                app_name="orchestrator_api",
                user_id=user_id,
                session_id=session_id,
                state={
                    "auth_token": current_user.get("token"),
                    "conversation_history": [],
                },
            )
        logger.info("Session ready", session_id=session_id)
        response = await process_chat_message(
            request, session,
            db_agent_configs=agent_configs,
            db_mcp_tool_configs=mcp_tool_configs,
        )
        return response
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(error=e, message="Error processing chat message")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/session/{session_id}")
async def get_session_info(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return the session info for a session (only if owned by current user)."""
    try:
        user_id = current_user["user_id"]
        user_id_uuid = uuid.UUID(user_id)

        # Validate session ownership
        is_owner = await validate_session_ownership(db, user_id_uuid, session_id)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Session does not belong to you")

        session = await session_service.get_session(
            app_name="orchestrator_api",
            user_id=user_id,
            session_id=session_id,
        )
        return {"session": session}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=e, message="Error retrieving session info")
        raise HTTPException(status_code=500, detail=str(e))
