from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.filesystem_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import filesystem_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="filesystem_assistant",
    description="A filesystem operations agent that explores, reads, writes, searches, and manages files and directories on the local system.",
    instruction=SYSTEM_PROMPT,
    tools=[filesystem_toolset],
    port=8003,
    agent_dir=AGENT_DIR,
)
