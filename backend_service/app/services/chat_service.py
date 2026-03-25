from typing import Optional

from google.adk.sessions import Session
from google.genai import types
from google.adk.runners import Runner

from app.agentic.orchestrator.agent import RootAgent
from app.services.session_service import session_service
from app.models.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatResponseContent,
    HITLRequestedItem,
)
from app.utils.logging import logger


async def process_chat_message(
    request: ChatRequest,
    session: Session,
    db_agent_configs: Optional[list[dict]] = None,
    db_mcp_tool_configs: Optional[list[dict]] = None,
) -> ChatResponse:
    """Process a chat message through the orchestrator.

    Args:
        request: The chat request from the user.
        session: The ADK session for this conversation.
        db_agent_configs: Optional agent configs loaded from DB (per-user).
        db_mcp_tool_configs: Optional MCP tool configs loaded from DB (per-user).
    """
    try:
        # Create the message content
        if request.content.message:
            logger.info("Received user message")
            new_message = types.Content(
                role="user", parts=[types.Part(text=request.content.message)]
            )
        elif request.content.hitl_approval:
            logger.info("Received HITL approval response")
            hitl_update = []
            for hitl_obj in request.content.hitl_approval:
                # Create ToolConfirmation response
                tool_confirmation_response = {
                    "confirmed": hitl_obj.confirmed,
                    "payload": hitl_obj.payload,
                }
                hitl_update.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=hitl_obj.function_id,
                            name=hitl_obj.function_name,
                            response=tool_confirmation_response,
                        )
                    )
                )
            new_message = types.Content(role="user", parts=hitl_update)
        else:
            raise ValueError(
                "Either message or hitl_approval must be provided in the request content."
            )

        # Run the agent and collect response
        response_text = None
        hitl_requests = []
        events = []
        root_agent = RootAgent(
            session.state.get("auth_token"),
            request,
            db_agent_configs=db_agent_configs,
            db_mcp_tool_configs=db_mcp_tool_configs,
        )
        app = root_agent.get_root_app()
        runner = Runner(app=app, session_service=session_service)
        async for event in runner.run_async(
            user_id=request.user_id, session_id=session.id, new_message=new_message
        ):
            events.append(event)
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
                        hitl_requests.append(
                            HITLRequestedItem(
                                function_id=part.function_call.id,
                                function_name=part.function_call.name,
                                confirmed=part.function_call.args.get(
                                    "toolConfirmation", {}
                                ).get("confirmed", False),
                                payload=part.function_call.args.get(
                                    "originalFunctionCall", {}
                                ).get("args"),
                                hint=part.function_call.args.get(
                                    "toolConfirmation", {}
                                ).get("hint"),
                            )
                        )

        content = ChatResponseContent(
            message=response_text,
            metadata={"events": events},
            hitl_requested=hitl_requests,
        )

        return ChatResponse(
            user_id=request.user_id,
            session_id=request.session_id,
            content=content,
        )
    except Exception as e:
        logger.error(error=e, message="Error in process_chat_message")
        raise
