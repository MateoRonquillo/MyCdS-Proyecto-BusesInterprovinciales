# Evidencias de pruebas y CI — Semana 3

## Responsable y alcance

- Integrante N6: David Rodriguez.
- Actividad: pruebas de seguridad e integración continua.
- Rama: feature/pruebas-integracion-seguridad.
- PR real: #13.
- Referencia de planificación: PR-18.
- Estado de este avance: seguridad JWT y CI verificados.
- Pendiente: pruebas de reservas y disponibilidad de asientos.

## Trazabilidad

- PR: https://github.com/MateoRonquillo/MyCdS-Proyecto-BusesInterprovinciales/pull/13
- Ejecución de GitHub Actions: https://github.com/MateoRonquillo/MyCdS-Proyecto-BusesInterprovinciales/actions/runs/40447576001
- Commit evaluado: 6d398b0a3737b86ad35a1ce7a4451df5ee4a5da3
- Fecha de inicio de pytest: 26 de octubre de 2026, 23:03:25
  (hora de Ecuador continental).
- Archivo de evidencia: [pytest-seguridad.xml](pytest-seguridad.xml).

El XML fue descargado del artefacto resultados-pruebas-backend
de GitHub Actions. Se conserva su contenido original; únicamente
se cambió el nombre del archivo descargado.

## Resultados del reporte XML

| Indicador | Resultado |
| --- | --- |
| Pruebas ejecutadas | 23 |
| Fallos | 0 |
| Errores | 0 |
| Pruebas omitidas | 0 |
| Duración de pytest | 1,761 segundos |

La suite incluye cinco casos de API y dieciocho casos de
autenticación y seguridad. Ocho casos de seguridad fueron
agregados en este avance.

La duración indicada corresponde a pytest, no al workflow completo.

## Casos nuevos de seguridad

Se comprobó que el endpoint /api/v1/auth/me responda HTTP 401
ante los siguientes escenarios:

1. Token expirado.
2. Firma incorrecta.
3. Algoritmo no permitido.
4. Ausencia del identificador sub.
5. Identificador no convertible a un número.
6. Usuario inexistente.
7. Usuario inactivo.
8. Ausencia del campo de expiración exp.

## Defecto detectado y corrección

Durante la ejecución local previa a la corrección, un token
firmado con la clave de pruebas, asociado a un usuario activo
y sin el campo exp recibió HTTP 200 en lugar de HTTP 401.

Se modificó decode_access_token para exigir los campos exp
y sub, manteniendo HS256 como algoritmo permitido.

Después de la corrección, las 23 pruebas pasaron localmente.
El XML adjunto confirma que también pasaron en GitHub Actions.

El reporte adjunto corresponde a la ejecución posterior
a la corrección; no contiene el fallo inicial.

## Verificación del workflow

La ejecución vinculada terminó correctamente en sus tres trabajos:

- Pruebas del backend.
- Compilación del frontend.
- Validación de Docker Compose y construcción de la imagen del backend.

El XML acredita únicamente los resultados de pytest.
Los resultados de frontend e infraestructura se consultan
en la ejecución de GitHub Actions vinculada.

El workflow genera el reporte JUnit XML y lo publica como
artefacto con una retención configurada de 30 días. Esta copia
permite conservar los resultados en el repositorio.

## Limitaciones y pendientes

- Las pruebas del backend usan SQLite; no acreditan integración
  con MySQL.
- Aún no se han validado reservas, tarifas ni doble asignación
  de asientos mediante estas pruebas.
- La construcción de la imagen y validación de Compose no
  demuestran un despliegue ni el funcionamiento de todos
  los servicios juntos.
- Las ejecuciones mostraron advertencias que no impidieron
  su finalización; el XML no es un registro completo de ellas.
- Queda pendiente vincular la solicitud de cambio y completar
  las dos revisiones del PR.