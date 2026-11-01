from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.core_models import Frecuencia, Usuario
from app.schemas.tarifas import CalculoTarifaRequest, CalculoTarifaResponse
from app.services.tarifas import TipoPasajero, calcular_pasajero

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

    passenger_types = payload.tipos_pasajero or [
        TipoPasajero.GENERAL
    ] * (payload.cantidad_pasajeros or 1)
    unit_price = round(frequency.precio, 2)
    detail = []
    discount_total = 0.0
    fare_total = 0.0
    for passenger_type in passenger_types:
        base, discount, passenger_total = calcular_pasajero(frequency.precio, passenger_type)
        discount_total += float(discount)
        fare_total += float(passenger_total)
        detail.append({
            "tipo_pasajero": passenger_type,
            "precio_unitario": float(base),
            "descuento_porcentaje": 50 if passenger_type != TipoPasajero.GENERAL else 0,
            "descuento": float(discount),
            "total": float(passenger_total),
        })
    total_passengers = len(passenger_types)
    return CalculoTarifaResponse(
        frecuencia_id=frequency.id,
        cantidad_pasajeros=total_passengers,
        precio_unitario=unit_price,
        descuento_total=round(discount_total, 2),
        subtotal=round(unit_price * total_passengers, 2),
        total=round(fare_total, 2),
        detalle=detail,
    )
