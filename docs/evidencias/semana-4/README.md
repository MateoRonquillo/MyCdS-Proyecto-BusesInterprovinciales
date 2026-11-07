# Evidencias de integración - Semana 4

## 1. Responsable

- Integrante N.º 6.
- Proyecto: Sistema de Venta de Boletos y Control de Acceso.
- Rama: `feature/integracion-pruebas-rc1`.
- Fecha: 5 de noviembre de 2026.

## 2. Pruebas de integración

Se agregaron cinco pruebas automatizadas para verificar:

1. Un pago pendiente no permite descargar el boleto QR.
2. Un oficinista puede aprobar pagos y habilitar el QR.
3. Los montos incorrectos son rechazados.
4. No se permiten pagos pendientes duplicados.
5. Los pagos rechazados devuelven la reserva a pendiente.

## 3. Resultados de pytest

- Pruebas ejecutadas: 35.
- Pruebas aprobadas: 35.
- Fallos: 0.
- Advertencias: 2.

Evidencia: `pytest-integracion.xml`.

Las pruebas se ejecutaron utilizando SQLite.

## 4. Verificación de Docker y MySQL

- MySQL 8.0: contenedor saludable.
- Backend FastAPI: iniciado correctamente.
- Puerto de MySQL: 3307.
- Puerto de FastAPI: 8000.
- Endpoint `/api/v1/health`: respuesta correcta.

## 5. Migraciones Alembic

Se verificaron las migraciones de pagos, historial y boletos.

Versión actual: `a7c3e9d2f104 (head)`.

## 6. Pendientes

- Verificar GitHub Actions después del push.
- Las pruebas automatizadas todavía no se ejecutaron en MySQL.
- No se realizaron pruebas de concurrencia.

## 7. Conclusión

Se verificó la integración básica entre reservas, pagos y boletos QR mediante 35 pruebas automatizadas. También se comprobó el inicio del backend con Docker y MySQL.
