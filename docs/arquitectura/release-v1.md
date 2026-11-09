# Arquitectura y contratos de la candidata

## Componentes

Vue/Pinia consume `/api/v1`. En Compose, Nginx sirve la SPA, conserva las rutas
al recargar y reenvía `/api/` a FastAPI. La API usa SQLAlchemy con MySQL 8.
Alembic mantiene el esquema; la revisión nueva es `b10000000001`.

JWT de 30 minutos; contraseñas con Argon2. El registro público solo crea clientes.
Los roles internos se crean por CLI. Los comprobantes se guardan en MySQL como
imagen base64 privada y se consultan a través de autorización; no hay URL pública.
El límite es 2 MB decodificados y 16 millones de píxeles; solo PNG/JPEG reales.

## Endpoints incorporados o ampliados

| Ruta | Uso y autorización |
|---|---|
| `POST /auth/registro` | Crear cliente con cédula validada y contraseña |
| `/cooperativas`, `/rutas` | GET/POST/PUT/DELETE, administrador |
| `/buses`, `/frecuencias` | GET/POST/PUT/DELETE, admin o cooperativa propietaria |
| `/jornadas` | GET por fecha, POST y DELETE, admin o cooperativa propietaria |
| `/configuracion` | GET público, PUT solo admin |
| `/notificaciones` | GET del usuario, PATCH `/{id}/leer` solo propietario |
| `GET /viajes` | Búsqueda pública con segmentos, filtros y detalle de bus |
| `/reservas` | Crear, consultar, modificar/cancelar pendientes según propietario o rol |
| `POST /tarifas/calcular` | Precio por tramo y tipo calculado en servidor |
| `/pagos` | Registro y consulta según propiedad; revisión solo admin/oficinista |
| `GET /pagos/{id}/comprobante` | Archivo privado para propietario u oficina |
| `GET /boletos/{reserva_id}/descarga` | Boleto HTML descargable, solo autorizado |
| `GET /boletos/{reserva_id}/qr` | QR PNG, solo autorizado |
| `POST /boletos/validar` | Consulta de validez de abordaje sin consumir el boleto |
| `POST /boletos/abordar` | Registro persistente de acceso, único por boleto |

Contratos completos y esquemas: `/docs` y `/openapi.json` del backend.
Los errores conservan el sobre `error.code`, `error.message` y `error.details`.

## Disponibilidad y consistencia

Una ruta tiene origen (índice 0), paradas ordenadas y destino final. Las solicitudes
usan `origen_orden` inclusivo y `destino_orden` exclusivo. La reserva guarda ambos,
la identificación del pasajero y el precio vendido. Sin índices, cubre la ruta completa.

`ocupaciones_asientos` registra una fila por segmento de cada reserva activa.
Una restricción única en frecuencia, fecha, asiento y segmento impide superposiciones.
Crear/modificar reserva bloquea la frecuencia en MySQL y traduce conflictos a HTTP 409.
Cancelar o expirar libera las ocupaciones. La disponibilidad consulta la intersección
entre segmentos; dos tramos contiguos pueden reutilizar el mismo asiento.

El pago pasa a `PENDIENTE` y la reserva a `PAGO_EN_REVISION` en una transacción.
Aprobar bloquea pago y reserva, genera un solo boleto y registra historial y notificación.
Rechazar devuelve la reserva a `PENDIENTE`. La revisión de descuento necesita
`descuento_verificado=true`. El QR contiene un código aleatorio, sin datos personales.
El acceso se registra con una restricción única por boleto para impedir repetición.

La API de estados de reserva ya no permite omitir el flujo de pagos para confirmar.

## Compatibilidad y límites

La migración conserva reservas históricas como tramo completo, copia la identidad
del comprador, crea ocupaciones y elimina índices redundantes heredados. Desactiva
las frecuencias sin referencia ANT hasta su revisión. La reversión exige restaurar
el respaldo; el esquema previo no representa reservas distintas del mismo asiento
para segmentos contiguos.

La fecha identifica el día de salida de la frecuencia desde su origen. En esta
candidata, planificar rutas que crucen medianoche o varias salidas diarias por bus
requiere revisión operativa: no existe un motor de intervalos de flota ni calendario
multidía. La hoja manual soporta una salida diaria por unidad.

No hay integración con ANT, Registro Civil o bancos, envío de correo, devolución
bancaria ni comprobante tributario. El enunciado permite notificaciones en la app;
estas se almacenan transaccionalmente y se consultan desde compras.


## Ampliación de paneles

Las consultas `/panel/resumen`, `/panel/opciones` y `/panel/manifiesto` mantienen
el alcance por rol y cooperativa. `/ventas/presencial` emite reserva, pago y boleto
en una transacción con clave de reintento. `/ubicaciones` y `/destinos` abastecen
los selectores de provincias y ciudades. El documento `docs/release/paneles-y-temas.md`
describe contratos, interfaz y pruebas de esta ampliación.
