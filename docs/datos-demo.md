# Datos y credenciales de demostración

Carga **optativa** para el entorno local. Nunca se ejecuta automáticamente al
levantar los contenedores ni forma parte del provisionamiento de producción.

## Arranque sin colisión con MySQL local

La base del contenedor se publica por defecto en `127.0.0.1:3307`. El puerto
interno sigue siendo `db:3306`; no es necesario detener el MySQL del equipo.

```sh
docker compose up --build -d --wait
docker compose exec backend python -m app.db.seed --demo
```

Si también utiliza 3307 otro servicio, cambie `MYSQL_HOST_PORT` en `.env` y ajuste
el puerto de `DATABASE_URL` para herramientas ejecutadas fuera de Docker.
Los datos existentes se conservan. No utilice `down -v` para resolver puertos.

## Acceso

Interfaz: `http://localhost:8080/login`.
Contraseña inicial común de estas cuentas: **`DemoPasajes2026!`**.

| Rol | Correo | Alcance |
|---|---|---|
| Administrador | `admin.demo@example.test` | Catálogos, configuración y paneles |
| Cooperativa | `cooperativa.demo@example.test` | Buses y frecuencias de DEMO Sierra Centro |
| Oficinista | `oficinista.demo@example.test` | Ventanilla, reservas y revisión de pagos |
| Cliente | `cliente.demo@example.test` | Compras y notificaciones del cliente principal |
| Chofer | `chofer.demo@example.test` | Abordaje de DEMO Sierra Centro |
| Ayudante | `ayudante.demo@example.test` | Abordaje de DEMO Sierra Centro |
| Segundo cliente | `cliente2.demo@example.test` | Compras independientes para comprobar privacidad |

Son cuentas y cédulas sintéticas, con correos del dominio reservado `example.test`.
No representan personas ni cooperativas reales. Las referencias ANT y bancarias
incluyen DEMO y carecen de validez operativa.

Puede elegir otra contraseña **antes de crear las cuentas**:

```sh
docker compose exec -e DEMO_PASSWORD='Una-clave-demo-propia-2026!' backend python -m app.db.seed --demo
```

La repetición de la carga conserva las contraseñas, perfiles, estados y revisiones
existentes: no restablece cuentas. Si el correo o la cédula sintética colisiona con
una cuenta ajena, la operación falla y revierte la transacción. No habilitar estas
cuentas conocidas en un entorno de producción.

## Catálogos de ejemplo

Tres cooperativas, seis buses con asientos normales/VIP, cuatro rutas y seis
frecuencias. Los buses tienen marcas de chasis Volvo/Mercedes-Benz y carrocerías
Marcopolo/Busscar. Las hojas de trabajo asignan una salida por unidad y día.

| Ruta | Paradas | Salida | Tarifa completa |
|---|---|---|---|
| Quito–Cuenca | Latacunga, Riobamba | 08:00 y 13:00 | USD 20 / 22 |
| Ambato–Quito | Latacunga | 10:00 y 16:00 | USD 5 / 6 |
| Guayaquil–Cuenca | Directo | 09:00 | USD 12 |
| Quito–Loja | Latacunga, Riobamba, Cuenca | 06:00 | USD 30 |

Puede buscar también entre paradas, por ejemplo Latacunga–Riobamba o Latacunga–Cuenca.
Los precios se calculan proporcionalmente al tramo en el servidor.

## Compras precargadas

Las fechas se calculan al ejecutar el comando en la zona America/Guayaquil.

| Escenario | Fecha relativa | Uso |
|---|---|---|
| Pendiente de pago | Mañana | Registrar depósito o transferencia desde Mis compras |
| Transferencia por revisar | Mañana | Revisar su comprobante con la cuenta oficinista |
| Boleto preferencial aprobado | Mañana | Descargar el boleto y consultar el descuento de ejemplo |
| Tramo Latacunga–Riobamba | Mañana | Ver precio y ocupación solo del tramo comprado |
| Abordaje disponible hoy | Hoy | Descargar QR y registrar un acceso con chofer/ayudante |
| Abordaje ya utilizado hoy | Hoy | Verificar el rechazo de un segundo acceso |
| Reserva cancelada | Mañana | Consultar historial y asiento liberado |
| Depósito rechazado | Pasado mañana | Corregir y volver a presentar el pago |
| Compra del segundo cliente | Mañana | Comprobar que no aparece en el historial del principal |

El nombre del pasajero identifica cada escenario con `DEMO:`. Para probar una
aprobación o un rechazo, entrar como oficinista y abrir la bandeja de pagos.
Para probar abordaje, descargar el QR con el cliente principal y usar el contenido
del QR o un lector externo en `/abordaje`. Las cuentas de personal solo aceptan
boletos de su cooperativa y fecha actual; un QR ya usado se rechaza.

El archivo [comprobante sintético](ejemplos/comprobante-demo.png) sirve para
practicar cargas. Está marcado «SIN VALIDEZ BANCARIA» y no registra ningún movimiento
bancario real. La aprobación demo es únicamente una simulación de negocio en esta base.

Reejecutar el comando el mismo día no duplica las compras. En días distintos añade
los escenarios de las nuevas fechas y conserva el historial anterior. No limpia
compras ni restablece escenarios que el usuario ya haya modificado.
