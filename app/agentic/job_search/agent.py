from pathlib import Path

from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.job_search_agent import SYSTEM_PROMPT
from app.agentic.shared.agent_utils import build_a2a_agent
from app.agentic.tools.custom_tools import write_to_disk
from app.agentic.tools.mcp_toolset import duckduckgo_toolset

a2a_app, root_agent = build_a2a_agent(
    agent_name="job_search_assistant",
    description="A job search agent that finds job opportunities on the web and saves the results to disk.",
    instruction=SYSTEM_PROMPT,
    tools=[duckduckgo_toolset, write_to_disk],
    port=8001,
    agent_dir=AGENT_DIR,
)
