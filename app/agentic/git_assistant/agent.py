from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.git_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import git_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="git_assistant",
    description="A Git operations agent that analyzes commit history, shows diffs, manages branches, performs blame analysis, and investigates code changes in Git repositories.",
    instruction=SYSTEM_PROMPT,
    tools=[git_toolset],
    port=8009,
    agent_dir=AGENT_DIR,
)
