# Validación de infraestructura para staging

## 1. Descripción

Se incorporaron verificaciones automáticas para comprobar
las pruebas del backend, la compilación del frontend y la
configuración de Docker Compose.

Estas verificaciones permiten detectar errores antes de
integrar los cambios en la rama develop.

## 2. Componentes verificados

- Backend FastAPI: pruebas automáticas con pytest.
- Frontend Vue 3: instalación y compilación con Vite.
- Docker Compose: validación de la configuración.
- Backend Docker: construcción de la imagen.

## 3. Configuración del entorno

El archivo .env.example contiene las variables necesarias
para preparar el entorno local.

Para crear el archivo de configuración, ejecutar desde
Git Bash:

    cp .env.example .env

Después, reemplazar las contraseñas de ejemplo por
contraseñas locales seguras.

El archivo .env no debe subirse al repositorio.

## 4. Pruebas locales realizadas

### Backend

Comando:

    cd backend
    python -m pytest -v

Resultado obtenido:

- 5 pruebas aprobadas.
- 0 pruebas fallidas.
- 1 advertencia de dependencia.

### Frontend

Comandos:

    npm ci --prefix frontend
    npm run build --prefix frontend

Resultado obtenido:

- Instalación correcta de dependencias.
- 48 módulos transformados.
- Compilación finalizada correctamente.

### Docker Compose

Comando:

    docker compose --env-file .env.example config --quiet

Resultado obtenido:

- Configuración válida.
- Código de salida 0.

### Imagen del backend

Comando:

    docker compose --env-file .env.example build backend

Resultado obtenido:

- Imagen construida correctamente.
- Nombre: plataforma-buses-backend:latest
- Código de salida 0.

## 5. Automatización mediante GitHub Actions

El archivo .github/workflows/ci.yml contiene tres trabajos:

1. Pruebas automáticas del backend.
2. Compilación del frontend.
3. Validación de infraestructura y construcción del backend.

Las verificaciones se ejecutarán automáticamente al
abrir o actualizar un Pull Request dirigido a develop,
si se modifican las rutas configuradas en el workflow.

## 6. Estado del despliegue

Las comprobaciones locales se completaron correctamente.

Está pendiente verificar la ejecución de los tres trabajos
en GitHub Actions y definir el destino de staging.

No se ha realizado todavía un despliegue remoto.

## 7. Control de cambios

Los cambios se desarrollan en una rama independiente
y se integrarán en develop mediante un Pull Request.

El PR deberá contar con las pruebas aprobadas y con
dos revisores, según las normas del proyecto.
