# Evidencias locales de release

Reportes JUnit generados al verificar los cambios de la candidata el 2026-11-07.

| Archivo | Entorno | Resultado |
|---|---|---|
| pytest-python312.xml | Docker, Python 3.12, SQLite para suite aislada | 46 aprobadas, 1 omitida |
| pytest-mysql80.xml | Docker, Python 3.12 y MySQL 8.0 | 10 aprobadas |
| pytest-mysql84.xml | Python 3.14 y MySQL 8.4 temporal | 10 aprobadas |

La prueba omitida en SQLite se ejecutó en MySQL. Ver ../../release/validacion.md
para alcance, otras comprobaciones y límites. No son reportes de GitHub Actions
ni evidencia de aceptación visual o despliegue productivo.

`pytest-demo.xml` contiene las dos pruebas adicionales de la carga optativa de
cuentas y compras de demostración. Estas pruebas no están incluidas en el reporte
histórico de 46 aprobadas; corresponden al ajuste posterior del arranque y seed.

## Ampliación de paneles y temas

| Reporte | Resultado |
|---|---|
| pytest-paneles.xml | 55 aprobadas, 2 omitidas en SQLite |
| pytest-paneles-mysql.xml | 18 aprobadas, incluidas las dos de concurrencia |
| vitest-paneles.xml | 12 componentes/escenarios aprobados en DOM simulado |
| migracion-paneles.txt | Datos heredados preservados y esquema actualizado a b10000000002 |

La compilación Docker también ejecutó las 12 pruebas de componentes dentro de
Node 22 antes de construir los assets. Ver ../../release/paneles-y-temas.md y
../../release/validacion.md. No se acreditan pruebas visuales ni de hardware.

## Revisión del 8 de noviembre de 2026

- `vitest-tema-oscuro-integridad.xml`: 24 aprobadas.
- `pytest-integridad-2026-11-08.xml`: 55 aprobadas y 2 omitidas en SQLite.
- `pytest-integridad-mysql-2026-11-08.xml`: 18 aprobadas; incluye concurrencia.
- `integridad-datos-2026-11-08.json`: comprobación local de solo lectura, sin incidencias.

Ver ../../release/revision-paneles-2026-11-08.md para alcance y límites.
