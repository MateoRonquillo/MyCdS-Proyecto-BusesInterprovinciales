# Registro de cambios de la candidata 1.0.0

Fecha de preparación: 2026-11-07 (America/Guayaquil).
Base local: rama develop, commit `fa8e69e`.

No se han creado issues, PR, tags ni solicitudes en Jira durante esta preparación.
Los identificadores siguientes son **locales propuestos**, no claves de Jira ni
aprobaciones del comité. El equipo debe asignar responsables y decisiones reales.

| ID local | Solicitud propuesta | Impacto | Evidencia |
|---|---|---|---|
| CR-LOCAL-01 | Completar operación y venta por tramos | Esquema, permisos, reservas, comprobantes, QR y notificaciones | Migración b10000000001, test_release.py, JUnit |
| CR-LOCAL-02 | Sustituir pantallas simuladas por operaciones reales | Interfaz de todos los roles y contrato API | Build del frontend y código de vistas |
| CR-LOCAL-03 | Preparar ejecución y validación de release | Docker, Nginx, CI, bootstrap y comprobación de migración | Evidencias de pruebas y validacion.md |
| CR-LOCAL-04 | Completar documentación y trazabilidad | Manuales, informe, licencia propuesta y plantillas | Matriz, guía de commits y archivos .github |

## Procedimiento de auditoría del equipo

Para cada ID, abrir una solicitud real y registrar problema, impacto, criterios de
aceptación y responsable. Designar el comité de uno o dos integrantes. El comité
registra la decisión y sus condiciones. Enlazar issue, rama, commits, PR, revisión
y evidencia de pruebas. No marcar aprobada una solicitud sin la decisión real.

En Jira, preparar un dashboard con solicitudes por estado, responsable, prioridad
y versión, y una lista de cambios aprobados pendientes de despliegue. Exportar el
reporte o capturar el dashboard con fecha y enlazarlo en esta carpeta. Documentar
rechazos y correcciones, además de solicitudes aprobadas.

## Resultado de preparación

Se completó código y documentación local y se ejecutaron verificaciones técnicas
registradas en docs/release/validacion.md. La aceptación funcional del equipo,
publicación de PR y autorización de la release siguen pendientes. El PDF adjunto
no aporta los nombres del comité, plantilla institucional ni las resoluciones ANT;
no se inventaron esos datos.

## Solicitudes locales adicionales propuestas

- CR-LOCAL-05: mejorar paneles, temas, venta presencial atómica y control de abordaje.
- CR-LOCAL-06: sustituir entrada manual por selección geográfica de provincias y ciudades.

Estos identificadores siguen siendo propuestas locales: no son solicitudes reales
de Jira ni decisiones del comité. Su implementación y verificación se documentan
en `docs/release/paneles-y-temas.md`, con los reportes adicionales de la carpeta
de evidencias. La guía de commits incorpora el nuevo alcance.
