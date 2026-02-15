from fastapi import FastAPI
from dotenv import load_dotenv

from app.core.config import settings
from app.api.v1.router import api_v1_router

load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
