# Casos de prueba del módulo de reservas

## 1. Objetivo

Documentar los casos de prueba del módulo de reservas del Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador, para verificar que las operaciones funcionen correctamente.

## 2. Casos de prueba

| ID | Prueba | Procedimiento | Resultado esperado |
|---|---|---|---|
| CP-01 | Crear reserva | Registrar una reserva con datos válidos | La reserva se registra correctamente |
| CP-02 | Consultar reserva | Buscar una reserva existente | Se muestra la información de la reserva |
| CP-03 | Modificar reserva | Actualizar los datos de una reserva permitida | Los cambios se guardan correctamente |
| CP-04 | Cancelar reserva | Cancelar una reserva existente | La reserva cambia al estado cancelado |
| CP-05 | Seleccionar asiento | Elegir un asiento disponible | El asiento queda asociado a la reserva |
| CP-06 | Asiento ocupado | Intentar reservar un asiento ocupado | El sistema impide duplicar la reserva |
| CP-07 | Datos incompletos | Intentar reservar sin completar los campos obligatorios | El sistema muestra un mensaje de validación |
| CP-08 | Disponibilidad | Consultar asientos disponibles | Se muestran los asientos disponibles |

## 3. Criterios de aceptación

- El sistema debe registrar correctamente las reservas válidas.
- No debe permitir reservar asientos ocupados.
- Debe validar los datos obligatorios.
- Debe permitir consultar las reservas registradas.
- Debe aplicar las reglas establecidas para modificaciones y cancelaciones.

## 4. Registro de resultados

| Caso de prueba | Estado | Evidencia |
|---|---|---|
| CP-01 a CP-08 | Pendiente de ejecución | Por adjuntar |

Los casos de prueba se ejecutarán cuando las funcionalidades correspondientes estén disponibles.

## 5. Conclusión

Estos casos de prueba permiten verificar las principales funcionalidades del módulo de reservas, identificar posibles errores y mejorar la calidad del sistema.