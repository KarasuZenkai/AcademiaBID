# Entrega de Academia BID por GitHub

Este documento describe qué debe subir el responsable funcional a GitHub y qué debe entregar por separado al equipo de infraestructura. El repositorio se mantiene privado.

## Subir a GitHub

Subir el código fuente y sólo archivos sin secretos:

```text
backend/
frontend/
docs/
docker-compose.yml
.gitignore
backend/.env.example
frontend/.env.example
README.md
```

Cuando se prepare la contenerización de producción, también se subirán los siguientes archivos:

```text
backend/Dockerfile
frontend/Dockerfile
docker-compose.prod.yml
nginx/default.conf
.dockerignore
README-DEPLOY.md
```

El equipo de infraestructura tomará este repositorio desde GitHub para importarlo o clonarlo en GitLab. El responsable funcional no requiere acceso a GitLab.

## No subir a GitHub

```text
backend/.env
frontend/.env.local
node_modules/
.next/
backend/.venv/
datos o respaldos de PostgreSQL
secretos, contraseñas, tokens, llaves SSH o certificados
```

Los ejemplos `.env.example` sí se suben, porque sólo describen nombres de variables y no contienen valores reales.

## Entregar por canal seguro a infraestructura

El archivo [SOLICITUD_INFRAESTRUCTURA.txt](SOLICITUD_INFRAESTRUCTURA.txt) se puede copiar a un ticket, correo corporativo o herramienta de solicitudes. No incluye secretos.

Los valores reales de configuración se proporcionan sólo por el canal seguro indicado por infraestructura. Ellos los cargan como variables protegidas y enmascaradas en su plataforma de despliegue.

## Validaciones antes de compartir el repositorio

- Confirmar que el repositorio GitHub sea privado.
- Confirmar que `backend/.env` y `frontend/.env.local` no aparezcan en cambios a subir.
- Confirmar que los archivos `.env.example` no contengan valores reales.
- Rotar el secreto de Microsoft Entra antes de producción.
- Compartir la URL del repositorio y la rama `main` con infraestructura.
- Confirmar el dominio productivo para registrar el Redirect URI en Microsoft Entra.

## Estado actual

La aplicación ya corre localmente con frontend Next.js, backend FastAPI y PostgreSQL. PostgreSQL tiene una composición Docker local. Los contenedores de frontend/backend, proxy HTTPS y pipeline de despliegue todavía deben agregarse antes de la entrega final de producción.
