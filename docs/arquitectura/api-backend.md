# API del backend

## Ejecucion local

Desde `backend/`, instalar las dependencias y ejecutar:

```sh
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`. La especificacion OpenAPI
se publica en `/openapi.json` y la interfaz interactiva en `/docs`.

## Estructura

- `app/main.py`: crea la aplicacion y registra routers y manejadores de errores.
- `app/api/router.py`: agrupa rutas bajo el prefijo versionado `/api/v1`.
- `app/api/routes/`: contiene los routers por recurso.
- `app/core/errors.py`: define el formato comun de errores.

## Endpoint inicial

### `GET /api/v1/health`

Comprueba que la API esta activa.

Respuesta `200`:

```json
{
  "status": "ok"
}
```

## Reservas

Los endpoints de reservas requieren un token Bearer. Los clientes solo pueden
consultar y modificar sus propias reservas; los administradores y oficinistas
pueden consultar todas. La creación recibe `frecuencia_id`, `fecha_viaje` (ISO
`YYYY-MM-DD`) y `asiento`; el usuario autenticado y el precio vigente de la
frecuencia se asignan en el servidor.

- `POST /api/v1/reservas`: crear una reserva pendiente (`201`).
- `GET /api/v1/reservas`: listar reservas permitidas para el usuario.
- `GET /api/v1/reservas/{id}`: consultar una reserva.
- `PUT /api/v1/reservas/{id}`: cambiar el asiento de una reserva pendiente.
- `DELETE /api/v1/reservas/{id}`: cancelar una reserva pendiente (`204`).

La API rechaza frecuencias inactivas, fechas pasadas, asientos fuera de la
capacidad del bus y asientos ya ocupados para la misma frecuencia y fecha.
Una cancelación conserva el registro y libera el asiento.

## Cálculo de tarifas

`POST /api/v1/tarifas/calcular` requiere autenticación. Recibe `frecuencia_id`
y, opcionalmente, `cantidad_pasajeros` (de 1 a 10) para tarifa general o una
lista `tipos_pasajero` de 1 a 10 elementos. Los tipos son `GENERAL`,
`ADULTO_MAYOR`, `DISCAPACIDAD`, `NINO_ADOLESCENTE` y `ESTUDIANTE`. No se pueden
enviar ambos campos de pasajeros a la vez. La respuesta incluye el desglose por pasajero,
precio unitario, descuento acumulado, subtotal y total en USD, redondeados a
dos decimales. Los tipos preferenciales reciben un descuento del 50%; la tarifa
general no recibe descuento. El descuento estudiantil queda sujeto a la
acreditación y condiciones vigentes. Al crear una reserva se puede enviar
`tipo_pasajero`; se guarda la categoría y el precio resultante como valor
histórico. La documentación legal y los requisitos de elegibilidad deben
validarse en el proceso de venta.

El [Reglamento a la Ley de Transporte Terrestre, artículo 46](https://www.gob.ec/sites/default/files/regulations/2019-12/REGLAMENTO_A_LA_LEY_DE_TRANSPORTE_TERRESTRE_TRANSITO_Y_SEGURIDAD_VIAL.pdf)
establece la tarifa del 50% para discapacidad, estudiantes de básica y
bachillerato bajo ciertas condiciones, niñas, niños, adolescentes y mayores de
65 años. La [Ley Orgánica de las Personas con Discapacidad, artículo 87](https://www.asambleanacional.gob.ec/es/system/files/ley_organica_de_discapacidades.pdf)
también reconoce la tarifa preferencial del 50% para transporte terrestre.

## Errores

Los errores HTTP se devuelven con el estado original y un cuerpo `error` que
incluye `code` y `message`. Los errores de validacion responden `422` y agregan
`details`, una lista con la ubicacion, el mensaje y el tipo del campo invalido.
Los errores inesperados responden `500` sin exponer detalles internos al cliente.
