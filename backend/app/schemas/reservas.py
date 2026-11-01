from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.services.tarifas import TipoPasajero


class ReservaCreate(BaseModel):
    frecuencia_id: int = Field(gt=0)
    fecha_viaje: date
    asiento: int = Field(gt=0)
    tipo_pasajero: TipoPasajero = TipoPasajero.GENERAL


class ReservaUpdate(BaseModel):
    asiento: int = Field(gt=0)


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    frecuencia_id: int
    fecha_viaje: date
    asiento: int
    tipo_pasajero: TipoPasajero
    precio: float
    estado: str

class AsientoEstado(BaseModel):
    numero: int
    ocupado: bool


class DisponibilidadAsientosResponse(BaseModel):
    frecuencia_id: int
    fecha_viaje: date
    capacidad_total: int
    asientos_ocupados: list[int]
    asientos_disponibles: list[int]
    mapa_asientos: list[AsientoEstado]