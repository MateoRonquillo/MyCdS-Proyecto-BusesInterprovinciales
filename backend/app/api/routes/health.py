from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Comprobar el estado de la API")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}