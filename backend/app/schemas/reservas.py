from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ReservaCreate(BaseModel):
    frecuencia_id: int = Field(gt=0)
    fecha_viaje: date
    asiento: int = Field(gt=0)


class ReservaUpdate(BaseModel):
    asiento: int = Field(gt=0)


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    frecuencia_id: int
    fecha_viaje: date
    asiento: int
    precio: float
    estado: str
