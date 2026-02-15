import os
from typing import Optional
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.apps import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool

from app.agentic.prompts_library.orchestrator_agent import SYSTEM_PROMPT
from app.agentic.tools.custom_tools import check_prime, check_weather, find_file_path
from app.agentic.adapters.mcp_adapter import McpAdapter
from app.agentic.adapters.remote_a2a_adapter import RemoteA2aAdapter
from app.utils.logging import logger

AGENT_MODEL = os.getenv("AGENT_MODEL")


approval_find_file_path = FunctionTool(func=find_file_path, require_confirmation=True)
approval_check_prime = FunctionTool(func=check_prime, require_confirmation=True)


class RootAgent():

    def __init__(self, auth_token: Optional[str] = None) -> None:
        self._auth_token = auth_token
        self.mcp_adapter = McpAdapter(auth_token=self._auth_token)
        self.remote_a2a_adapter = RemoteA2aAdapter(auth_token=self._auth_token)
        self.root_agent = self.get_root_agent()
        
    def get_root_agent(self):
        logger.info("Building root agent with sub-agents and tools...")
        sub_agents_list = self.remote_a2a_adapter.get_remote_agents()
        mcp_toolset = self.mcp_adapter.get_mcp_tool_sets()
        tools_list = [approval_check_prime, check_weather, approval_find_file_path]
        tools_list.extend(mcp_toolset)
        root_agent = Agent(
            name="Supervisor",
            model=LiteLlm(model=AGENT_MODEL),
            description="An agent that either hands off tasks to specialized sub-agents or uses tools directly to accomplish the overall goal effectively.",
            instruction=SYSTEM_PROMPT,
            # before_agent_callback=update_agents_and_tools_before,
            # after_agent_callback=update_agents_and_tools_after,
        )
        if sub_agents_list:
            root_agent.sub_agents = sub_agents_list
            logger.info("Added sub-agents to root agent.", number_of_sub_agents=len(sub_agents_list), sub_agents_list=[agent.name for agent in sub_agents_list])
        else:
            logger.info("No sub-agents found to add to root agent.")
        if tools_list:
            root_agent.tools = tools_list
            logger.info("Added tools to root agent.", number_of_tools=len(tools_list), tools_list=tools_list)
        else:
            logger.info("No tools found to add to root agent.")
        return root_agent
    
    def get_root_app(self):
        logger.info("Building root app with updated agents and tools...")
        app = App(
            name="Supervisor",
            root_agent=self.root_agent,
            resumability_config=ResumabilityConfig(
                is_resumable=True
            )
        )
        return app