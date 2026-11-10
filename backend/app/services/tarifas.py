from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum


CENTAVO = Decimal("0.01")
DESCUENTO_PREFERENCIAL = Decimal("0.50")


class TipoPasajero(StrEnum):
    GENERAL = "GENERAL"
    ADULTO_MAYOR = "ADULTO_MAYOR"
    DISCAPACIDAD = "DISCAPACIDAD"
    NINO_ADOLESCENTE = "NINO_ADOLESCENTE"
    ESTUDIANTE = "ESTUDIANTE"


def calcular_pasajero(precio_unitario: float, tipo: TipoPasajero) -> tuple[Decimal, Decimal, Decimal]:
    """Calcula precio base, descuento y total para un pasajero."""
    precio = Decimal(str(precio_unitario)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    tasa = DESCUENTO_PREFERENCIAL if tipo != TipoPasajero.GENERAL else Decimal("0")
    descuento = (precio * tasa).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return precio, descuento, precio - descuento


def calcular_importe(precio_unitario: float, cantidad: int) -> tuple[Decimal, Decimal]:
    """Devuelve el precio unitario y el total redondeados a centavos."""
    precio = Decimal(str(precio_unitario)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    total = (precio * cantidad).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return precio, total
