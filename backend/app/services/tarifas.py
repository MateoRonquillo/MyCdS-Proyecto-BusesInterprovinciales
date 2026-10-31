from decimal import Decimal, ROUND_HALF_UP


CENTAVO = Decimal("0.01")


def calcular_importe(precio_unitario: float, cantidad: int) -> tuple[Decimal, Decimal]:
    """Devuelve el precio unitario y el total redondeados a centavos."""
    precio = Decimal(str(precio_unitario)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    total = (precio * cantidad).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return precio, total
