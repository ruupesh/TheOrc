import os
import sys
import json
from datetime import datetime
from pathlib import Path

from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Get the path to the 'src' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..')

# Add the tools and prompts directories to the system path
tools_dir = os.path.join(src_dir, 'tools')
prompts_dir = os.path.join(src_dir, 'prompts_library')

sys.path.append(tools_dir)
sys.path.append(prompts_dir)

# Import from the new paths
from job_search_agent import SYSTEM_PROMPT
from custom_tools import write_to_disk
from mcp_toolset import duckduckgo_toolset

from dotenv import load_dotenv
load_dotenv()

AGENT_MODEL = os.getenv("AGENT_MODEL")


# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / "conversation_logs"
LOGS_DIR.mkdir(exist_ok=True)


def log_conversation_history(callback_context: CallbackContext):
    """
    Callback to log the conversation history (session events) to a file.
    
    This captures what history the remote agent receives from the calling agent.
    For A2A agents, this will show the reconstructed message parts sent by RemoteA2aAgent.
    """
    try:
        session = callback_context._invocation_context.session
        invocation_id = callback_context._invocation_context.invocation_id
        
        # Create a structured log of the conversation
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session.id,
            "invocation_id": invocation_id,
            "app_name": session.app_name,
            "user_id": session.user_id,
            "last_update": str(session.last_update_time),
            "state": dict(session.state),  # Current session state
            "events": []
        }
        
        # Add all events (conversation history)
        for event in session.events:
            event_data = {
                "invocation_id": event.invocation_id,
                "author": event.author,
                "content": None,
                "actions": None,
            }
            
            # Extract content if available
            if event.content and event.content.parts:
                event_data["content"] = {
                    "role": event.content.role,
                    "parts": []
                }
                for part in event.content.parts:
                    part_info = {}
                    if part.text:
                        part_info["text"] = part.text
                    if part.function_call:
                        part_info["function_call"] = {
                            "name": part.function_call.name,
                            "args": part.function_call.args if hasattr(part.function_call, 'args') else None
                        }
                    if part.function_response:
                        part_info["function_response"] = {
                            "name": part.function_response.name,
                            "response": str(part.function_response.response)[:200]  # Truncate long responses
                        }
                    event_data["content"]["parts"].append(part_info)
            
            # Extract actions if available
            if event.actions:
                event_data["actions"] = {
                    "state_delta": event.actions.state_delta if event.actions.state_delta else None,
                    "transfer_to_agent": event.actions.transfer_to_agent if hasattr(event.actions, 'transfer_to_agent') and event.actions.transfer_to_agent else None,
                }
            
            log_data["events"].append(event_data)
        
        # Write to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOGS_DIR / f"conversation_{session.id}_{timestamp}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"[Conversation Log] History written to: {log_file}")
        print(f"[Conversation Log] Total events: {len(session.events)}")
        
    except Exception as e:
        print(f"[Conversation Log] Error logging history: {e}")


# Dummy secret token for validation (replace with real JWT validation in production)
DUMMY_SECRET_TOKEN = "THIS-IS-RUPESH"


def validate_jwt(token: str) -> bool:
    """
    Dummy JWT validator.
    
    In production, replace this with actual JWT validation logic:
    - Decode and verify the JWT signature
    - Check token expiration
    - Validate claims (issuer, audience, etc.)
    
    For now, simply checks if the token matches the dummy secret.
    """
    return token == DUMMY_SECRET_TOKEN


class JWTValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate JWT tokens in incoming A2A requests.
    
    Allows:
    - Health check and agent card endpoints without authentication
    - Authenticated requests with valid JWT token
    
    Blocks:
    - Requests to protected endpoints without valid token
    
    NOTE: Currently, the ADK's a2a_request_meta_provider does not pass
    headers to the HTTP layer. This middleware will validate headers
    when authentication is properly implemented at the transport level.
    For now, we allow requests without auth for development purposes.
    Set REQUIRE_AUTH=true environment variable to enforce authentication.
    """

    # Endpoints that don't require authentication
    EXEMPT_PATHS = {
        "/.well-known/agent.json",       # Agent card endpoint (legacy)
        "/.well-known/agent-card.json",  # Agent card endpoint (current)
        "/health",
    }
    
    async def dispatch(self, request: Request, call_next):
        # Allow exempt paths without authentication
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        print(f"[JWT Middleware] Request path: {request.url.path}, Auth header: {auth_header}")
        
        # Extract token from "Bearer <token>" format
        if not auth_header.startswith("Bearer "):
            print("[JWT Middleware] Invalid Authorization format")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid Authorization header format. Use 'Bearer <token>'"}
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Validate the token
        if not validate_jwt(token):
            print(f"[JWT Middleware] Invalid token: {token[:20]}...")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"}
            )
        
        print("[JWT Middleware] Token validated successfully")
        return await call_next(request)


root_agent = Agent(
    name="job_search_assistant",
    model=LiteLlm(model=AGENT_MODEL),
    description="A job search agent that finds job opportunities on web and saves the results to disk.",
    instruction=SYSTEM_PROMPT,
    tools=[duckduckgo_toolset, write_to_disk],
    before_agent_callback=log_conversation_history,  # Log history before agent processes
)


# Create the A2A app and add JWT validation middleware
a2a_app = to_a2a(root_agent, port=8001)
a2a_app.add_middleware(JWTValidationMiddleware)
# a2a_app.add_websocket_route