from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.report_writer_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import fetch_toolset
from app.agentic.tools.custom_tools import write_to_disk
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="report_writer",
    description="A report writing agent that researches topics from the web and produces well-structured, professional reports saved to disk in Markdown format.",
    instruction=SYSTEM_PROMPT,
    tools=[fetch_toolset, write_to_disk],
    port=8011,
    agent_dir=AGENT_DIR,
)
