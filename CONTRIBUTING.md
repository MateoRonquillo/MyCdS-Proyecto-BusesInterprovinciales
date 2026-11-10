# Guía de contribución

## 1. Objetivo

Establecer las normas de colaboración y control de cambios para el desarrollo del Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador, garantizando una organización adecuada del código, la documentación y las contribuciones del equipo.

## 2. Flujo de trabajo con Git

El proyecto utiliza GitFlow para organizar el desarrollo mediante ramas:

- `main`: contiene las versiones estables del sistema.
- `develop`: integra los cambios aprobados durante el desarrollo.
- `feature/*`: permite desarrollar nuevas funcionalidades.
- `release/*`: prepara versiones para su publicación.
- `hotfix/*`: corrige errores críticos de versiones estables.

Estas son las únicas familias de ramas admitidas. Los cambios de documentación,
pruebas y mantenimiento se realizan en `feature/*`, o dentro de `release/*` si
forman parte de su estabilización. No se utilizan prefijos alternativos.

Las ramas `feature/*` nacen de `develop` y se integran en `develop`. Las ramas
`release/*` nacen de `develop` y al aprobarse se integran en `main` y `develop`.
Las ramas `hotfix/*` nacen de `main` y se reintegran en `main` y `develop`.
La publicación se identifica con un tag de versión aprobado por el equipo.

Cada integrante debe trabajar en una rama independiente y evitar modificar directamente `main` o `develop`.

## 3. Convención de commits

Los commits deben ser descriptivos y seguir el formato de Conventional Commits:

`tipo(alcance): descripción`

Tipos principales:

- `feat`: incorporación de funcionalidades.
- `fix`: corrección de errores.
- `docs`: cambios en la documentación.
- `style`: modificaciones de formato o estilos.
- `refactor`: reorganización del código sin cambiar su comportamiento.
- `test`: incorporación o modificación de pruebas.
- `chore`: tareas de mantenimiento o configuración.

Ejemplos:

- `feat(auth): implementar inicio de sesión`
- `fix(reservas): corregir validación de asientos`
- `docs: actualizar guía de contribución`

## 4. Gestión de solicitudes en Jira

Las actividades y solicitudes de cambio deben registrarse en Jira antes de iniciar su desarrollo.

Cada solicitud debe contener:

- Título y descripción de la actividad.
- Integrante responsable.
- Prioridad y criterios de aceptación.
- Estado de avance y evidencias correspondientes.

Los cambios deben vincularse con su solicitud de Jira para mantener la trazabilidad.

## 5. Pull Requests y revisiones

Para incorporar cambios al proyecto se debe:

1. Actualizar la rama base correspondiente.
2. Crear una rama de trabajo.
3. Realizar commits funcionales y descriptivos.
4. Publicar la rama en GitHub.
5. Crear un Pull Request hacia la rama correspondiente.
6. Asignar los dos revisores establecidos en el plan de trabajo.
7. Corregir las observaciones realizadas durante la revisión.
8. Fusionar los cambios cuando cumplan los criterios de aprobación.

No se deben fusionar cambios con conflictos pendientes ni sin las revisiones requeridas.

## 6. Normas de colaboración

- Mantener una comunicación respetuosa y profesional.
- Respetar las responsabilidades asignadas a cada integrante.
- No incluir contraseñas, credenciales ni información personal real.
- Documentar los cambios relevantes.
- Verificar el funcionamiento antes de solicitar una revisión.
- Evitar modificar archivos de otros integrantes sin coordinación.
- Cumplir las normas establecidas en `CODE_OF_CONDUCT.md`.

## 7. Resolución de conflictos

Cuando se produzcan conflictos de integración, los integrantes involucrados deben revisar las diferencias, coordinar una solución y verificar que los cambios funcionen correctamente.

Los conflictos relevantes y su resolución deben quedar documentados como parte del control de cambios.