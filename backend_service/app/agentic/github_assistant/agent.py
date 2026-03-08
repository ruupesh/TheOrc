from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.github_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import github_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="github_assistant",
    description="A GitHub operations agent that manages repositories, issues, pull requests, and performs code search across GitHub.",
    instruction=SYSTEM_PROMPT,
    tools=[github_toolset],
    port=8002,
    agent_dir=AGENT_DIR,
)
