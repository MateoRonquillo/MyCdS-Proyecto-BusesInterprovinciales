# Registro de cambios

## 1.0.0-rc.1 — candidata local, sin publicar

### Funciones

- Catálogos persistentes, gestión por cooperativa y hoja diaria con días de parada.
- Reservas y disponibilidad por segmentos entre paradas, con control de concurrencia.
- Datos del pasajero, asientos NORMAL/VIP y detalle/filtros de bus.
- Registro de clientes, pagos con comprobante y revisión manual del descuento.
- Historial, notificaciones, descarga de boleto HTML/QR y abordaje de un solo uso.
- Nombre, logo, color y contactos de soporte configurables.
- Pantallas de administración y oficina conectadas a la API.

### Paneles y experiencia de uso

- Navegación y resúmenes por rol, formularios con relaciones por nombre y tablas filtrables.
- Selector persistente de tema claro, oscuro y del sistema, aplicado a interfaz pública y paneles.
- Provincia/ciudad en búsquedas, con conexiones y paradas realmente configuradas.
- Venta presencial atómica con clave de reintento y protección ante emisión duplicada.
- Revisión por pago, lista de pasajeros y verificación del QR antes de confirmar el acceso.
- Boleto descargable con diseño de impresión y hora de salida del tramo comprado.
- Pruebas de componentes y de concurrencia ampliadas.

### Entrega

- Frontend servido por Nginx en Docker y comprobaciones de salud de servicios.
- CI para ramas develop/main/release con pruebas MySQL y migración de datos heredados.
- Documentación de operación, matriz de requisitos, licencia MIT propuesta,
  metadatos de cita y plantillas de issues/PR.

### Compatibilidad

- Migración `b10000000001`: preservar respaldo antes de aplicar.
- Frecuencias antiguas sin resolución ANT quedan inactivas hasta completar su revisión.
- Confirmar reservas exige aprobar el pago; no basta cambiar el estado directamente.
- Base anterior incompatible con reservas por segmentos: reversión mediante respaldo.

Ver docs/release/validacion.md para pruebas realizadas y pendientes.
