from pydantic import BaseModel, Field


class CalculoTarifaRequest(BaseModel):
    frecuencia_id: int = Field(gt=0)
    cantidad_pasajeros: int = Field(default=1, ge=1, le=10)


class CalculoTarifaResponse(BaseModel):
    frecuencia_id: int
    cantidad_pasajeros: int
    moneda: str = "USD"
    precio_unitario: float
    subtotal: float
    total: float
