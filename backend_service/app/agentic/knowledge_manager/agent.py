from pathlib import Path
from dotenv import load_dotenv

AGENT_DIR = Path(__file__).parent
ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(ROOT_ENV_PATH)
load_dotenv(AGENT_DIR / ".env", override=True)

from app.agentic.prompts_library.knowledge_manager_agent import SYSTEM_PROMPT
from app.agentic.tools.mcp_toolset import memory_toolset
from app.agentic.shared.agent_utils import build_a2a_agent

a2a_app, root_agent = build_a2a_agent(
    agent_name="knowledge_manager",
    description="A knowledge management agent that maintains a persistent knowledge graph with entities, observations, and relations for long-term memory.",
    instruction=SYSTEM_PROMPT,
    tools=[memory_toolset],
    port=8005,
    agent_dir=AGENT_DIR,
)
