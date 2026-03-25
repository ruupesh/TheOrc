from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logging import configure_logging, get_logger
from app.api.v1.router import api_v1_router
from app.db.database import engine
from app.db.base import Base

# Import all models so they register with Base.metadata
import app.models.user  # noqa: F401
import app.models.user_session  # noqa: F401
import app.models.agent  # noqa: F401
import app.models.mcp_tool  # noqa: F401
import app.models.marketplace  # noqa: F401


configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    logger.info("app_startup")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
