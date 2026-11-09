import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.errors import register_exception_handlers


def create_app() -> FastAPI:
    application = FastAPI(
        title="Gestion de Pasajes Ecuador API",
        description="API para la gestion de pasajes en Ecuador.",
        version="1.0.0-rc.1",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    register_exception_handlers(application)
    return application


app = create_app()