from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.reservas import router as reservas_router
from app.api.routes.tarifas import router as tarifas_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(reservas_router)
api_router.include_router(tarifas_router)
