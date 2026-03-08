from google.adk.sessions import InMemorySessionService
from google.adk_community.sessions import RedisSessionService

session_service = RedisSessionService()
