from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.time_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import time_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="time_assistant",
    description="A time and timezone agent that provides current times, converts between timezones, helps schedule meetings across zones, and performs date/time calculations.",
    instruction=SYSTEM_PROMPT,
    tools=[time_toolset],
    port=8010,
    agent_dir=AGENT_DIR,
)
