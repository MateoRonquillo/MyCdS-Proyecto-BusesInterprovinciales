# Flujo de solicitudes y control de cambios en Jira

## 1. Objetivo

Establecer el procedimiento para registrar, asignar, desarrollar, revisar y cerrar solicitudes de cambio del Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador, manteniendo la trazabilidad entre Jira y GitHub.

## 2. Tipos de solicitudes

- **Tarea:** actividad técnica o de documentación.
- **Historia de usuario:** funcionalidad requerida por un usuario del sistema.
- **Error (Bug):** problema detectado durante el desarrollo o las pruebas.
- **Mejora:** modificación destinada a optimizar una funcionalidad existente.
 
## 3. Registro de solicitudes

Cada solicitud debe contener:

- Identificador asignado por Jira.
- Título y descripción.
- Tipo de solicitud y prioridad.
- Integrante responsable.
- Criterios de aceptación.
- Evidencias o archivos relacionados, cuando corresponda.

## 4. Estados de las solicitudes

Las actividades seguirán el siguiente flujo, siempre que los estados estén configurados en el tablero de Jira:

1. **Por hacer (To Do):** solicitud registrada y pendiente de desarrollo.
2. **En progreso (In Progress):** integrante trabajando en la actividad.
3. **En revisión (In Review):** cambios enviados mediante Pull Request para revisión.
4. **Finalizado (Done):** cambios aprobados, integrados y verificados.

Cuando se soliciten correcciones, la actividad regresará a En progreso.

## 5. Desarrollo y control de versiones

Cada integrante debe:

1. Seleccionar la actividad asignada en Jira.
2. Crear una rama de trabajo basada en la rama correspondiente.
3. Realizar los cambios y commits convencionales.
4. Publicar la rama en GitHub.
5. Crear un Pull Request asociado con la solicitud de Jira.
6. Solicitar la revisión de los dos integrantes asignados.

Se recomienda incluir la clave de Jira en la descripción del Pull Request para facilitar la trazabilidad.

## 6. Revisión y aprobación

Los revisores deben verificar:

- Cumplimiento de los criterios de aceptación.
- Calidad y organización de los cambios.
- Ausencia de errores evidentes y conflictos pendientes.
- Documentación correspondiente.

Las observaciones deben corregirse antes de integrar los cambios.

## 7. Cierre de solicitudes

Una solicitud podrá marcarse como finalizada cuando el trabajo haya sido revisado, aprobado, fusionado en la rama correspondiente y verificado.

Se deberá registrar el enlace del Pull Request y las evidencias de cumplimiento.

## 8. Responsabilidades

- **Responsable de la tarea:** desarrolla y documenta los cambios.
- **Revisores:** comprueban el cumplimiento de los requisitos.
- **Gestores de cambios:** supervisan el seguimiento de las solicitudes, las revisiones y la integración de cambios.