from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.browser_automation_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import puppeteer_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="browser_automation",
    description="A browser automation agent that navigates web pages, takes screenshots, fills forms, extracts content, and performs web testing using a headless Chrome browser.",
    instruction=SYSTEM_PROMPT,
    tools=[puppeteer_toolset],
    port=8008,
    agent_dir=AGENT_DIR,
)
