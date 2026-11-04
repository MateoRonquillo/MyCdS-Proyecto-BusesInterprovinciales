from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MetodoPago(StrEnum):
    EFECTIVO = "EFECTIVO"
    DEPOSITO = "DEPOSITO"
    TRANSFERENCIA = "TRANSFERENCIA"


class EstadoPago(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class PagoCreate(BaseModel):
    reserva_id: int = Field(gt=0)
    metodo_pago: MetodoPago
    monto: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    referencia: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def require_reference_for_transfer(self):
        if self.metodo_pago != MetodoPago.EFECTIVO and not (self.referencia or "").strip():
            raise ValueError("La referencia es obligatoria para depósitos y transferencias")
        if self.referencia is not None:
            self.referencia = self.referencia.strip() or None
        return self


class RechazoPagoRequest(BaseModel):
    motivo: str = Field(min_length=1, max_length=255)

    @model_validator(mode="after")
    def validate_reason(self):
        self.motivo = self.motivo.strip()
        if not self.motivo:
            raise ValueError("El motivo del rechazo es obligatorio")
        return self


class PagoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reserva_id: int
    registrado_por_id: int
    revisado_por_id: int | None
    metodo_pago: MetodoPago
    monto: float
    referencia: str | None
    estado: EstadoPago
    motivo_rechazo: str | None
    creado_en: datetime
    revisado_en: datetime | None
