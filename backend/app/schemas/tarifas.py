from pydantic import BaseModel, Field, model_validator

from app.services.tarifas import TipoPasajero


class CalculoTarifaRequest(BaseModel):
    frecuencia_id: int = Field(gt=0)
    cantidad_pasajeros: int | None = Field(default=None, ge=1, le=10)
    tipos_pasajero: list[TipoPasajero] | None = Field(default=None, min_length=1, max_length=10)

    @model_validator(mode="after")
    def validate_passengers(self):
        if self.cantidad_pasajeros is None and self.tipos_pasajero is None:
            self.cantidad_pasajeros = 1
        if self.cantidad_pasajeros is not None and self.tipos_pasajero is not None:
            raise ValueError("Use cantidad_pasajeros o tipos_pasajero, pero no ambos")
        return self


class ImportePasajero(BaseModel):
    tipo_pasajero: TipoPasajero
    precio_unitario: float
    descuento_porcentaje: int
    descuento: float
    total: float


class CalculoTarifaResponse(BaseModel):
    frecuencia_id: int
    cantidad_pasajeros: int
    moneda: str = "USD"
    precio_unitario: float
    descuento_total: float
    subtotal: float
    total: float
    detalle: list[ImportePasajero]
