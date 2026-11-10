from datetime import date, time

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.services.tarifas import TipoPasajero


class ReservaCreate(BaseModel):
    frecuencia_id: int = Field(gt=0)
    fecha_viaje: date
    asiento: int = Field(gt=0)
    tipo_pasajero: TipoPasajero = TipoPasajero.GENERAL
    origen_orden: int = Field(default=0, ge=0)
    destino_orden: int | None = Field(default=None, gt=0)
    pasajero_nombre: str | None = Field(default=None, min_length=3, max_length=100)
    pasajero_cedula: str | None = Field(default=None, min_length=10, max_length=10)


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
    origen_orden: int = 0
    destino_orden: int = 1
    pasajero_nombre: str | None = None
    pasajero_cedula: str | None = None

class AsientoEstado(BaseModel):
    numero: int
    ocupado: bool
    tipo: str = "NORMAL"


class DisponibilidadAsientosResponse(BaseModel):
    frecuencia_id: int
    fecha_viaje: date
    capacidad_total: int
    asientos_ocupados: list[int]
    asientos_disponibles: list[int]
    mapa_asientos: list[AsientoEstado]

class HistorialCompraItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reserva_id: int
    pasajero_nombre: str | None = None
    pasajero_cedula: str | None = None
    frecuencia_id: int
    cooperativa: str
    numero_disco: str
    origen: str
    destino: str
    hora_salida: time
    fecha_viaje: date
    asiento: int
    tipo_pasajero: str
    precio: float
    estado: str

class EstadoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGO_EN_REVISION = "PAGO_EN_REVISION"
    PAGADA = "PAGADA"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"

class ReservaEstadoUpdate(BaseModel):
    estado: EstadoReserva