# Flujo de solicitudes de cambio y trazabilidad

## 1. Objetivo

Establecer un procedimiento para registrar, evaluar, aprobar, implementar y cerrar las solicitudes de cambio del Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador, garantizando la trazabilidad mediante Jira, Git y GitHub.

## 2. Registro de solicitudes

Cada solicitud de cambio deberá registrarse en Jira e incluir los siguientes datos:

- Identificador de la solicitud.
- Título y descripción del cambio.
- Tipo de cambio: correctivo, adaptativo, perfectivo o preventivo.
- Prioridad e impacto.
- Responsable asignado.
- Fecha de creación.
- Estado de la solicitud.
- Evidencias y observaciones.

## 3. Flujo de control de cambios

El proceso de gestión de cambios comprende las siguientes etapas:

1. **Solicitud:** se registra el cambio en Jira.
2. **Evaluación:** se analiza su impacto, prioridad y viabilidad.
3. **Aprobación:** los responsables autorizan o rechazan el cambio.
4. **Implementación:** se desarrolla el cambio en una rama independiente.
5. **Verificación:** se realizan pruebas y revisiones del código.
6. **Cierre:** se documentan los resultados y se actualiza el estado en Jira.

## 4. Trazabilidad de cambios

Para garantizar el seguimiento de cada cambio, se establecerá una relación entre los siguientes elementos:

**Solicitud Jira → Rama Git → Commit → Pull Request → Revisión → Merge → Cierre**

Cada Pull Request deberá identificar la solicitud de Jira relacionada y contar con las revisiones establecidas por el equipo.

## 5. Matriz de seguimiento de cambios

La siguiente tabla constituye una plantilla que deberá completarse con las solicitudes reales registradas en Jira.

| ID Jira | Descripción | Responsable | Prioridad | Estado | Pull Request |
|---|---|---|---|---|---|
| Por registrar | Por registrar | Por asignar | Por definir | Pendiente | Por vincular |

## 6. Evidencias

Las evidencias del proceso podrán incluir:

- Capturas de las solicitudes registradas en Jira.
- Historial de commits de Git.
- Pull Requests y revisiones realizadas en GitHub.
- Resultados de las pruebas.
- Registro de aprobación y cierre de los cambios.

## 7. Conclusión

La aplicación de un flujo estructurado de solicitudes de cambio permite mantener el control sobre las modificaciones realizadas al sistema, mejorar la colaboración entre los integrantes y garantizar la trazabilidad de cada actividad durante el desarrollo del proyecto.