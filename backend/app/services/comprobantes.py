import base64
import binascii
from io import BytesIO
from PIL import Image, UnidentifiedImageError


def validar_comprobante(valor: str | None):
    if valor is None:
        return None
    try:
        cabecera, contenido = valor.split(",", 1)
        if cabecera not in {"data:image/png;base64", "data:image/jpeg;base64"}:
            raise ValueError("Solo se permiten imágenes PNG o JPEG")
        datos = base64.b64decode(contenido, validate=True)
        if not 0 < len(datos) <= 2_000_000:
            raise ValueError("El comprobante debe tener hasta 2 MB")
        with Image.open(BytesIO(datos)) as imagen:
            if imagen.format not in {"PNG", "JPEG"} or imagen.width * imagen.height > 16_000_000:
                raise ValueError("Imagen inválida o demasiado grande")
            if (imagen.format == "PNG") != ("image/png" in cabecera):
                raise ValueError("El formato no coincide con el contenido")
            imagen.verify()
    except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Comprobante de imagen inválido") from exc
    return valor
