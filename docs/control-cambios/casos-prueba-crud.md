# Casos de prueba CRUD

## 1. Objetivo

Documentar los casos de prueba para verificar las operaciones de creación, consulta, actualización y eliminación de registros del Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador, con el propósito de identificar errores y comprobar el cumplimiento de los requisitos funcionales.

## 2. Alcance

Las pruebas estarán orientadas a las funcionalidades CRUD de los módulos del sistema que se encuentren implementados, como usuarios, rutas, buses y reservas.

## 3. Casos de prueba

| ID | Módulo | Operación | Procedimiento | Resultado esperado |
|---|---|---|---|---|
| CP-01 | Usuarios | Crear | Registrar un usuario con datos válidos | Usuario registrado correctamente |
| CP-02 | Usuarios | Consultar | Buscar un usuario existente | Se muestra la información registrada |
| CP-03 | Usuarios | Actualizar | Modificar los datos de un usuario | Los cambios se guardan correctamente |
| CP-04 | Usuarios | Eliminar | Eliminar un usuario existente | El registro se elimina o desactiva según las reglas del sistema |
| CP-05 | Rutas | Crear | Registrar una ruta con origen y destino | Ruta registrada correctamente |
| CP-06 | Rutas | Consultar | Consultar las rutas disponibles | Se muestra el listado de rutas |
| CP-07 | Rutas | Actualizar | Modificar la información de una ruta | Los cambios se reflejan en el sistema |
| CP-08 | Rutas | Eliminar | Eliminar una ruta permitida | La ruta deja de estar disponible |
| CP-09 | Buses | Crear | Registrar un bus con datos válidos | Bus registrado correctamente |
| CP-10 | Buses | Consultar | Buscar un bus registrado | Se muestra su información |
| CP-11 | Buses | Actualizar | Modificar los datos del bus | Información actualizada |
| CP-12 | Buses | Eliminar | Eliminar un bus permitido | Registro eliminado o desactivado |
| CP-13 | Reservas | Crear | Registrar una reserva válida | Reserva creada correctamente |
| CP-14 | Reservas | Consultar | Consultar una reserva existente | Se muestra el detalle de la reserva |
| CP-15 | Reservas | Actualizar | Modificar una reserva permitida | Reserva actualizada correctamente |
| CP-16 | Reservas | Eliminar | Cancelar una reserva | Reserva cancelada según las reglas del sistema |

## 4. Criterios de aceptación

Se considerará que una prueba es satisfactoria cuando:

- El sistema permita ejecutar la operación correspondiente.
- Los datos se almacenen o actualicen correctamente.
- Se respeten las validaciones establecidas.
- Se presenten mensajes apropiados al usuario.
- No se produzcan errores inesperados durante la operación.

## 5. Registro de resultados

Los casos de prueba definidos son propuestas de validación. Su ejecución deberá registrarse cuando las funcionalidades correspondientes estén disponibles.

| ID de prueba | Estado | Resultado obtenido | Evidencia |
|---|---|---|---|
| CP-01 a CP-16 | Pendiente de ejecución | Por registrar | Por adjuntar |

## 6. Gestión de incidencias

Cuando una prueba presente un resultado diferente al esperado, deberá registrarse una incidencia en Jira, incluyendo la descripción del error, pasos para reproducirlo, prioridad, responsable y evidencias correspondientes.

## 7. Conclusión

La documentación de casos de prueba CRUD permite establecer criterios de validación para las principales operaciones del sistema, facilitando la detección de errores, el seguimiento de incidencias y la mejora continua de la calidad del software.