from fastapi import APIRouter, Depends, HTTPException
from google.adk.runners import Runner

from app.agentic.orchestrator.agent import app
from app.core.security import get_current_user
from app.models.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat_message
from app.services.session_service import session_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatResponse:
    """
    Conversation endpoint.
    
    Receives a user message, processes it (Phase 2), and returns an assistant response.
    Requires a Bearer token in the Authorization header.
    """
    try:
        session_id = request.session_id
        user_id = request.user_id
        
        session = await session_service.get_session(
            app_name="orchestrator_api",
            user_id=user_id,
            session_id=session_id
        )
        print(f"Session retrieved: {session}")
        if not session:
            # Get or create session
            session = await session_service.create_session(
                app_name="orchestrator_api",
                user_id=user_id,
                session_id=session_id,
                state={"auth_token": current_user.get("token")}
            )
        print(f"Session: {session}")
        response = await process_chat_message(request, session)
        return response    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
