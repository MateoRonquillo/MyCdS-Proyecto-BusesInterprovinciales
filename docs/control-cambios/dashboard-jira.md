# Dashboard de Jira – Control de cambios y auditoría

## 1. Objetivo

Consolidar los indicadores de seguimiento de cambios, solicitudes e incidencias del proyecto **Plataforma de Control para Buses Interprovinciales**, para facilitar su revisión y auditoría.

## 2. Indicadores de seguimiento

| Indicador | Descripción | Fuente |
|---|---|---|
| Pull Requests | Cambios propuestos e integrados al proyecto | GitHub |
| Cambios aprobados | Solicitudes revisadas y aceptadas | GitHub / Jira |
| Cambios pendientes | Solicitudes que todavía requieren revisión | GitHub / Jira |
| Incidencias conocidas | Problemas y limitaciones identificados durante las pruebas | Documentación de QA |
| Evidencias de pruebas | Resultados de las verificaciones realizadas | `docs/evidencias/` |

## 3. Cambios registrados

Durante el desarrollo del sistema se han integrado funcionalidades relacionadas con:

- Gestión de reservas.
- Registro de pagos.
- Generación de boletos digitales con códigos QR.
- Venta de boletos en oficina.
- Validación de integridad de datos.
- Pruebas de integración.

Los cambios pueden consultarse en los Pull Requests del repositorio del proyecto.

## 4. Estado de las pruebas

Según las evidencias registradas para la semana 4:

- **35 pruebas aprobadas.**
- **0 pruebas fallidas.**
- **2 advertencias.**

También se identificaron verificaciones pendientes, como las pruebas sobre MySQL y los escenarios de concurrencia.

## 5. Seguimiento en Jira

Los indicadores anteriores sirven como base para el dashboard de Jira. Los identificadores de tickets, estados y enlaces específicos deben incorporarse una vez verificados en el tablero del equipo.

## 6. Conclusión

El seguimiento de los cambios y las evidencias de pruebas permite mantener la trazabilidad del proyecto, identificar actividades pendientes y facilitar la auditoría del desarrollo.