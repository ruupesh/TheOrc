from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.reasoning_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import sequential_thinking_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="reasoning_assistant",
    description="A reasoning and problem-solving agent that uses structured sequential thinking to break down complex problems, analyze decisions, debug issues, and plan tasks.",
    instruction=SYSTEM_PROMPT,
    tools=[sequential_thinking_toolset],
    port=8007,
    agent_dir=AGENT_DIR,
)
