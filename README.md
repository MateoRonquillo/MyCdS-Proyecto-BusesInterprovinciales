# Gestión de Pasajes Ecuador

Aplicación web para cooperativas de transporte interprovincial, clientes,
oficinistas y personal de abordaje. Candidata de primera versión: `1.0.0-rc.1`.

Vue 3, Pinia y Vite en el frontend; FastAPI, SQLAlchemy y Alembic en el backend;
MySQL 8 y Docker Compose para ejecución integrada. Las operaciones usan datos
persistentes por defecto.

## Ejecución con Docker

```sh
cp .env.example .env
# Editar .env: contraseñas propias y JWT_SECRET_KEY aleatoria de al menos 32 caracteres.
docker compose up --build -d
```

MySQL se publica en `127.0.0.1:3307` para evitar colisiones con una instalación local.
Interfaz: `http://localhost:8080`. API: `http://localhost:8000/docs`.
El backend aplica las migraciones al iniciar. Para crear la primera cuenta:

```sh
docker compose exec backend python -m app.db.bootstrap --nombre "Administrador" --correo admin@example.com --cedula CEDULA_VALIDA --rol admin
```

La contraseña se solicita sin mostrarla. No se crean cuentas ni claves automáticamente. Para probar todos los roles con
compras precargadas, siga la [carga opcional de demostración](docs/datos-demo.md).
El administrador crea cooperativas, rutas, buses y frecuencias desde `/operacion`.
Las cuentas internas se provisionan con el mismo comando y `--rol oficinista`,
`cooperativa`, `chofer` o `ayudante`; los tres últimos requieren `--cooperativa-id`.
Los clientes pueden registrarse en `/registro`.

## Desarrollo y pruebas

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
# DATABASE_URL debe apuntar a MySQL local; cargar también JWT_SECRET_KEY desde .env.
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

En otra terminal:

```sh
cd frontend
npm ci
npm run dev
```

Pruebas aisladas y compilación:

```sh
cd backend
DATABASE_URL=sqlite:// python -m pytest -v
cd ../frontend
npm ci
npm test
npm run build
```

SQLite se usa solo para pruebas; las migraciones están dirigidas a MySQL.
Los casos de bloqueo concurrente se ejecutan con `TEST_DATABASE_URL` contra una
base desechable; sus tablas se eliminan al terminar. Nunca usar una base real.

## Funciones

- CRUD con baja lógica de cooperativas, buses, rutas y frecuencias.
- Gestión de buses y frecuencias limitada a la cooperativa de la cuenta.
- Referencia de resolución ANT, paradas ordenadas y hoja de trabajo manual por día.
- Asientos normales/VIP, detalle de bus y filtros de búsqueda.
- Reservas por tramo con disponibilidad y precio proporcionales al recorrido.
- Ventanilla en efectivo; depósito/transferencia con comprobante PNG/JPEG privado.
- Revisión de pagos, historial, notificaciones dentro de la aplicación y boleto descargable.
- QR de un solo uso para registrar el abordaje en la fecha del viaje.
- Nombre, logo, color, redes y soporte configurables.

El boleto se descarga como HTML con información y QR, para conservarlo,
imprimirlo o guardarlo como PDF desde el navegador. La cámara de abordaje necesita
HTTPS y compatibilidad con `BarcodeDetector`; también admite lectores QR externos.
Las tarifas preferenciales conservan la política del prototipo (50%); se verifica
la cédula estructuralmente y el oficinista confirma el respaldo documental antes
de aprobar. No existe consulta automática al Registro Civil o a la ANT.

## Documentación y entrega

- [Revisión de tema oscuro e integridad](docs/release/revision-paneles-2026-11-08.md).
- [Paneles, temas y selección por provincia](docs/release/paneles-y-temas.md).
- [Datos y credenciales de demostración](docs/datos-demo.md).
- [Manual de usuario](docs/manual-usuario.md).
- [Arquitectura y contratos](docs/arquitectura/release-v1.md).
- [Matriz de requisitos del enunciado](docs/release/matriz-requisitos.md).
- [Despliegue, respaldo y reversión](docs/release/despliegue.md).
- [Cambios agrupados en commits propuestos](docs/release/commits-propuestos.md).
- [Validación y limitaciones](docs/release/validacion.md).
- [Informe académico editable](docs/informe/informe-proyecto.md).
- [Guion de defensa](docs/informe/defensa.md).
- [Contribución y Gitflow](CONTRIBUTING.md).

La publicación de `1.0.0` requiere validar el dominio HTTPS, datos operativos,
resoluciones, tarifas y evidencia de aceptación del equipo. No se ha desplegado
esta candidata en producción ni registrado decisiones en Jira/GitHub.

## Licencia y cita

Licencia MIT en [LICENSE](LICENSE); propuesta para revisión del equipo antes de
publicar. Los metadatos de cita están en [CITATION.cff](CITATION.cff). La fecha de
publicación y la versión definitiva deben incorporarse al crear el tag real.
