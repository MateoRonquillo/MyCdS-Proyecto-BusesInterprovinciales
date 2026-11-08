# Instrucciones del repositorio

## Flujo de ramas obligatorio

Por instrucción explícita del usuario, utilizar exclusivamente Gitflow en todas
las tareas futuras de este repositorio:

- `main`: versiones publicadas y estables.
- `develop`: integración del desarrollo.
- `feature/*`: funcionalidades, documentación, pruebas y mantenimiento; partir
  de `develop` y proponer integración a `develop`.
- `release/*`: estabilización de una versión; partir de `develop` y proponer
  integración final a `main` y `develop`.
- `hotfix/*`: correcciones urgentes de producción; partir de `main` y proponer
  integración a `main` y `develop`.

No utilizar ningún otro prefijo de rama. Esta regla incluye los nombres sugeridos
en documentación, comandos y propuestas de PR. Seguir también CONTRIBUTING.md.

Mantener agrupaciones de commits revisables según el alcance final del cambio.
No presentar ramas, commits, PR, aprobaciones o tags propuestos como si ya
existieran. Conservar los cambios locales del usuario al trabajar.
