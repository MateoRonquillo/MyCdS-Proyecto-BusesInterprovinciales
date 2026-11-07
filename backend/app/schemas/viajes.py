from datetime import date

from pydantic import BaseModel


class CooperativaViaje(BaseModel):
    id: int
    nombre: str
    color_principal: str | None = None
    logo_url: str | None = None


class ViajeResponse(BaseModel):
    id: int  # id de la frecuencia: es el que usa la reserva
    cooperativa: CooperativaViaje
    origen: str
    destino: str
    fecha: date
    hora_salida: str
    hora_llegada: str
    duracion_min: int
    precio: float
    asientos_disponibles: int
    tipo_bus: str | None = None


class ViajesResponse(BaseModel):
    items: list[ViajeResponse]
    total: int