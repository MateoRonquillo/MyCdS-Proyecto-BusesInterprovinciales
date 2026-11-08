from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.boletos import router as boletos_router
from app.api.routes.gestion import router as gestion_router
from app.api.routes.health import router as health_router
from app.api.routes.pagos import router as pagos_router
from app.api.routes.reservas import router as reservas_router
from app.api.routes.tarifas import router as tarifas_router
from app.api.routes.viajes import router as viajes_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(boletos_router)
api_router.include_router(health_router)
api_router.include_router(pagos_router)
api_router.include_router(reservas_router)
api_router.include_router(tarifas_router)
api_router.include_router(viajes_router)
api_router.include_router(gestion_router)
from app.api.routes.paneles import router as paneles_router
api_router.include_router(paneles_router)
from app.api.routes.destinos import router as destinos_router
api_router.include_router(destinos_router)
