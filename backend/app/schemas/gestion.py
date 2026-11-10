from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Entrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class CooperativaDatos(Entrada):
    nombre: str = Field(min_length=2, max_length=100)
    logo_url: str | None = Field(None, max_length=255, pattern=r"^https?://")
    color_principal: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    activo: bool = True


class BusDatos(Entrada):
    placa: str = Field(min_length=5, max_length=20)
    numero_disco: str = Field(min_length=1, max_length=10)
    capacidad_asientos: int = Field(ge=1, le=100)
    cooperativa_id: int = Field(gt=0)
    activo: bool = True
    chasis: str = Field("", max_length=80)
    carroceria: str = Field("", max_length=80)
    fotografia_url: str | None = Field(None, max_length=500, pattern=r"^https?://")
    asientos_vip: str = Field("", max_length=500, pattern=r"^\d*(,\d+)*$")

    @model_validator(mode="after")
    def validar_asientos(self):
        numeros = [int(n) for n in self.asientos_vip.split(",") if n]
        if any(n < 1 or n > self.capacidad_asientos for n in numeros) or len(numeros) != len(set(numeros)):
            raise ValueError("Asientos VIP fuera de capacidad o repetidos")
        return self


class ParadaDatos(Entrada):
    ciudad: str = Field(min_length=2, max_length=100)
    minutos: int = Field(gt=0)
    proporcion_tarifa: float = Field(gt=0, lt=1)


class RutaDatos(Entrada):
    origen: str = Field(min_length=2, max_length=100)
    destino: str = Field(min_length=2, max_length=100)
    duracion_estimada_horas: float = Field(gt=0, le=48)
    activo: bool = True
    paradas: list[ParadaDatos] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def orden_paradas(self):
        ciudades = [self.origen.casefold(), *[p.ciudad.casefold() for p in self.paradas], self.destino.casefold()]
        if len(set(ciudades)) != len(ciudades):
            raise ValueError("Las ciudades de la ruta deben ser distintas")
        minutos = [0, *[p.minutos for p in self.paradas], self.duracion_estimada_horas * 60]
        tarifas = [0, *[p.proporcion_tarifa for p in self.paradas], 1]
        if any(a >= b for a, b in zip(minutos, minutos[1:])) or any(a >= b for a, b in zip(tarifas, tarifas[1:])):
            raise ValueError("Las paradas deben tener tiempos y proporciones crecientes")
        return self


class FrecuenciaDatos(Entrada):
    ruta_id: int = Field(gt=0)
    bus_id: int = Field(gt=0)
    hora_salida: time
    precio: float = Field(gt=0, le=1000)
    activo: bool = True
    resolucion_ant: str = Field(min_length=3, max_length=150)


class JornadaDatos(Entrada):
    fecha: date
    bus_id: int = Field(gt=0)
    frecuencia_id: int | None = Field(None, gt=0)
    chofer_id: int | None = Field(None, gt=0)
    ayudante_id: int | None = Field(None, gt=0)


class TripulacionJornadaDatos(Entrada):
    chofer_id: int | None = Field(None, gt=0)
    ayudante_id: int | None = Field(None, gt=0)


class ConfiguracionDatos(Entrada):
    nombre: str = Field(min_length=2, max_length=100)
    logo_url: str | None = Field(None, max_length=500, pattern=r"^https?://")
    color_principal: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    soporte: str = Field("", max_length=150)
    redes_sociales: str = Field("", max_length=500)
