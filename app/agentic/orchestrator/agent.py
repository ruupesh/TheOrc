import sys
import os
from typing import Any
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from a2a.types import Message as A2AMessage
from google.adk.apps import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.long_running_tool import LongRunningFunctionTool
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import TransportProtocol


# Import from the new paths
from app.agentic.prompts_library.orchestrator_agent import SYSTEM_PROMPT
from app.agentic.tools.custom_tools import check_prime, check_weather, find_file_path
from app.agentic.tools.mcp_toolset import duckduckgo_toolset

from dotenv import load_dotenv
load_dotenv()

AGENT_MODEL = os.getenv("AGENT_MODEL")


def auth_token_provider(
    ctx: InvocationContext, 
    a2a_message: A2AMessage
) -> dict[str, Any]:
    """
    Provides authentication metadata to be sent with A2A requests.
    
    Retrieves the auth_token from session state and includes it
    in the Authorization header for the remote agent.
    
    NOTE: The current ADK a2a_request_meta_provider returns metadata
    that is used at the A2A protocol level, not HTTP headers.
    This is a known limitation - the metadata may not reach the
    HTTP transport layer as headers.
    """
    auth_token = ctx.session.state.get("auth_token") if ctx.session else None
    
    print(f"[Auth Token Provider] Session state: {ctx.session.state if ctx.session else 'No session'}")
    print(f"[Auth Token Provider] Auth token: {auth_token}")
    
    if auth_token:
        metadata = {
            "headers": {
                "Authorization": f"Bearer {auth_token}"
            },
            # Also include at top level for A2A metadata
            "authorization": f"Bearer {auth_token}"
        }
        print(f"[Auth Token Provider] Returning metadata: {metadata}")
        return metadata
    
    print("[Auth Token Provider] No auth token found in session state")
    return {}


async def update_agents_and_tools_before(callback_context: CallbackContext):
    print("Updating agents and tools based on callback context...")
    # print("Subagents before update:", callback_context._invocation_context.agent.sub_agents)
    print("Tools before update:", callback_context._invocation_context.agent.tools)
    # root_agent.tools = [GoogleSearchTool(bypass_multi_tools_limit=True)]
    # return None

async def update_agents_and_tools_after(callback_context: CallbackContext):
    print("Finalizing agents and tools after callback context...")
    # print("Subagents after update:", callback_context._invocation_context.agent.sub_agents)
    print("Tools after update:", callback_context._invocation_context.agent.tools)
    # return None


client_factory = ClientFactory(
    ClientConfig(
        # supported_transports=[TransportProtocol],
        use_client_preference=True,
        httpx_client=httpx.AsyncClient(
            headers={
                "Authorization": "Bearer THIS-IS-RUPESH",
                "Content-Type": "application/json"
            }
        )
    )
)

job_agent = RemoteA2aAgent(
    name="job_search_assistant",
    description="A job search agent that finds job opportunities and saves the results to disk.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    a2a_client_factory=client_factory
)

approval_find_file_path = FunctionTool(func=find_file_path, require_confirmation=True)
approval_check_prime = FunctionTool(func=check_prime, require_confirmation=True)

root_agent = Agent(
    name="Supervisor",
    model=LiteLlm(model=AGENT_MODEL),
    description="An agent that either hands off tasks to specialized sub-agents or uses tools directly to accomplish the overall goal effectively.",
    instruction=SYSTEM_PROMPT,
    # before_agent_callback=update_agents_and_tools_before,
    # after_agent_callback=update_agents_and_tools_after,
    sub_agents=[job_agent],
    tools=[approval_check_prime, check_weather, approval_find_file_path, duckduckgo_toolset],
)

app = App(
    name="Supervisor",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True
    )
)