# Manual de usuario de la candidata 1.0.0

## Cliente

1. Crear una cuenta desde Ingresar → Regístrate. Usar cédula válida y contraseña
   de al menos 12 caracteres.
2. Seleccionar provincia y ciudad de origen, provincia y ciudad de destino y fecha.
   Las opciones corresponden a conexiones configuradas, incluidas las paradas de una ruta. Filtrar cooperativa, horario, precio, asiento, chasis, carrocería y
   viaje directo/con paradas. Abrir «Ver bus» para consultar disco, placa y foto.
3. Seleccionar viaje, registrar pasajeros y elegir un asiento libre por pasajero.
   La numeración VIP se muestra antes de la selección; los otros son normales.
4. Confirmar las reservas. El precio se calcula en el servidor, incluido el tramo.
5. Ir a Mis compras y registrar cada pago por depósito o transferencia, con la
   referencia y una imagen PNG/JPEG de hasta 2 MB. Esperar la revisión manual.
6. Consultar el estado y las notificaciones en Mis compras. Si se rechaza el pago,
   corregir el comprobante y registrar uno nuevo. No crear otra reserva.
7. Descargar el boleto completo y/o QR al confirmarse el pago. El HTML se puede
   conservar e imprimir; el boleto sigue disponible desde el historial.
8. Presentar cédula y QR al abordar. «Comprar otro boleto» permite iniciar otra compra.

Se permite cancelar o cambiar el asiento de reservas pendientes mediante la API;
la pantalla de compras ofrece cancelación. Las compras de varios pasajeros crean
una reserva y un pago por asiento. Si una reserva falla, el cliente intenta cancelar
las creadas previamente; consulte Mis compras si se pierde la conexión.

## Oficinista

En Venta en ventanilla buscar un viaje real, seleccionar asiento y registrar nombre,
cédula y categoría. Cobrar el importe mostrado, verificar los documentos si solicita
una tarifa preferencial y pulsar «Confirmar cobro y emitir boleto». El cobro y boleto se registran en una sola transacción; si se pierde la respuesta, «Reintentar la misma venta» recupera la operación sin duplicarla.

En la bandeja se consultan reservas y pagos de clientes. «Ver comprobante» abre
el archivo privado; comprobar monto, referencia y movimiento en la cuenta bancaria
por el procedimiento de la cooperativa. Aprobar genera el boleto; rechazar exige
un motivo. No registrar dinero recibido basándose únicamente en la imagen.

Si falla un paso de una venta presencial, se muestra el ID de reserva para retomar
el pago desde la bandeja. No repetir la venta sin consultar su estado.

## Administrador y cooperativa

El administrador crea las cooperativas y rutas. El formulario ofrece ciudades
agrupadas por provincia y selectores con nombres para cooperativa, ruta y bus.
«Añadir parada» incorpora campos de ciudad, minutos desde origen y proporción
acumulada de tarifa (entre 0 y 1). Los tiempos y proporciones deben crecer.
Ejemplo: Latacunga, 90 minutos, 0.25. Para una tarifa completa de USD 20,
el primer tramo costará USD 5 y el restante USD 15.

Las cuentas de cooperativa gestionan únicamente sus buses y frecuencias.
Registrar la plantilla como capacidad y números VIP separados por comas. Completar
chasis, carrocería y fotografía mediante URL HTTP/HTTPS. La frecuencia requiere
ruta, bus propio, hora, tarifa y referencia de resolución ANT previamente revisada.

La hoja de trabajo se ingresa en «jornadas» para una fecha: bus y frecuencia asignada,
o frecuencia vacía para día de parada. La candidata admite una salida por bus y día
en la hoja. Sin hoja explícita se utiliza la frecuencia habitual. No permite una
planificación que deje reservas activas sin su frecuencia. El equipo debe organizar
las jornadas antes de habilitar la venta de la fecha.

«Desactivar» conserva las relaciones históricas. Los itinerarios con frecuencias
y las capacidades/asignaciones con reservas tienen protección para evitar cambiar
viajes vendidos: crear un registro nuevo para una nueva operación.

«Configuración» permite cambiar nombre, logo, color, soporte y redes sociales.
Recargar la aplicación para ver la nueva identidad.

## Chofer o ayudante

Usar Control de abordaje. Un lector QR externo puede escribir el JSON completo o
el código en el campo y enviar Enter. La cámara se ofrece cuando el navegador
admite detección QR y el sitio dispone de HTTPS (o localhost en desarrollo).

«Verificar boleto» muestra al pasajero, asiento y recorrido. Revisar la identidad
y pulsar «Confirmar abordaje» para registrar el acceso. La lista de pasajeros se
filtra por fecha, salida y estado de acceso.

El servidor exige boleto confirmado, pago aprobado, cooperativa de la cuenta,
fecha del viaje y ausencia de abordaje previo. Registra usuario y fecha de acceso.
El segundo intento se rechaza. Se requiere conexión con el servidor.

## Tema y navegación

La cabecera incluye el selector Claro / Oscuro / Sistema. La selección se conserva
en el dispositivo y se aplica tanto al sitio público como a los paneles internos.
En móvil, el botón de menú abre la navegación por rol. Las tablas permiten buscar,
filtrar y desplazarse horizontalmente cuando sea necesario. Ver detalles de las
mejoras en `docs/release/paneles-y-temas.md`.
