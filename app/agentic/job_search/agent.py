import os
import sys

from google.adk.agents.llm_agent import Agent
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
src_dir = os.path.join(current_dir, '..', '..')

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
)


# Create the A2A app and add JWT validation middleware
a2a_app = to_a2a(root_agent, port=8001)
a2a_app.add_middleware(JWTValidationMiddleware)
a2a_app.add_websocket_route