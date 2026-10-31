from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.core_models import Frecuencia, Usuario
from app.schemas.tarifas import CalculoTarifaRequest, CalculoTarifaResponse
from app.services.tarifas import calcular_importe

router = APIRouter(prefix="/tarifas", tags=["tarifas"])


@router.post(
    "/calcular",
    response_model=CalculoTarifaResponse,
    summary="Calcular el importe de una tarifa",
)
def calculate_fare(
    payload: CalculoTarifaRequest,
    db: Session = Depends(get_db),
    _user: Usuario = Depends(get_current_user),
) -> CalculoTarifaResponse:
    frequency = db.get(Frecuencia, payload.frecuencia_id)
    if frequency is None or not frequency.activo:
        raise HTTPException(status_code=404, detail="Frecuencia no encontrada o inactiva")

    unit_price, total = calcular_importe(frequency.precio, payload.cantidad_pasajeros)
    return CalculoTarifaResponse(
        frecuencia_id=frequency.id,
        cantidad_pasajeros=payload.cantidad_pasajeros,
        precio_unitario=float(unit_price),
        subtotal=float(total),
        total=float(total),
    )
