# Academia BID

MVP local de una plataforma interna de capacitación corporativa. Esta primera entrega implementa únicamente la **Fase 1**: estructura, configuración, PostgreSQL local, FastAPI, CORS y una interfaz Next.js que comprueba el estado de la API.

## Requisitos

- Un runtime Docker compatible (Docker Desktop o Colima) para PostgreSQL 16
- Python 3.9 o superior
- Node.js 20 o superior

## Ejecutar en local

### 1. PostgreSQL

```bash
docker compose up -d
```

La base se expone en `localhost:5432`, con base `academia_bid` y usuario `academia`. Las credenciales de desarrollo están en `docker-compose.yml`; no usar estos valores fuera de local.

### 2. Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

En Windows, active el entorno con `.venv\\Scripts\\activate`.

- API: <http://localhost:8000>
- Health: <http://localhost:8000/health>
- Swagger: <http://localhost:8000/docs>

`GET /health` devuelve `200` solo cuando PostgreSQL responde. Si la base no está disponible devuelve `503`, para que el frontend no informe un estado engañoso.

### 3. Frontend

En otra terminal:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Abra <http://localhost:3000>. La página inicial consulta `GET /health` mediante la capa `frontend/lib/api/health.ts`.

## Estructura

```text
academia-bid/
├── backend/        # FastAPI y SQLAlchemy 2.x
├── frontend/       # Next.js App Router, TypeScript y Tailwind
├── docs/           # Documentación de las próximas fases
└── docker-compose.yml  # Solo PostgreSQL 16
```

## Estado y siguientes pasos

La Fase 2 ya incluye el esquema relacional, la migración inicial de Alembic y un seed local idempotente. Aún no hay autenticación, APIs de catálogo, integración Entra/Graph ni reproducción de contenido: pertenecen a fases posteriores. En particular, la integración real con SharePoint requerirá validar documentación oficial, permisos y OBO antes de escribirla.

## Identidad local (Fase 3)

Mientras `AUTH_PROVIDER=local`, el backend usa los usuarios sembrados y acepta el header de desarrollo `X-Dev-User-Id`. Si se omite, usa `LOCAL_DEFAULT_USER_ID`. El selector del frontend guarda el usuario elegido en el navegador y solo se renderiza con `NEXT_PUBLIC_AUTH_PROVIDER=local`.

Al establecer `AUTH_PROVIDER=entra`, el backend devuelve `501` hasta que se implemente y valide la integración real con Microsoft Entra ID; nunca interpreta el header de desarrollo en ese modo.

## Administración local (Fase 5)

Abra `http://localhost:3000/admin` y seleccione **Administrador** en el selector de desarrollo. El panel muestra los UUID requeridos para crear el siguiente nivel de contenido. La API valida el rol `ADMIN` en el backend y registra cada creación, actualización y cambio de publicación en `audit_logs`.

Para las lecciones `VIDEO`, capture únicamente `sharepoint_site_id`, `sharepoint_drive_id` y `sharepoint_item_id`. La conexión a Microsoft Graph y la reproducción se implementarán después; no se guarda contenido multimedia en la base.

## Video local (Fase 6)

Con `MEDIA_PROVIDER=local`, `POST /api/lessons/{id}/playback` devuelve la URL del fixture `backend/media/demo.mp4`; el archivo se sirve como `/media/demo.mp4` y no se versiona. Para obtenerlo en un checkout nuevo, ejecute `cd backend && sh scripts/download-demo-media.sh`. Abra una lección `VIDEO` desde el catálogo para probar el reproductor HTML5.

Con `MEDIA_PROVIDER=sharepoint`, el endpoint devuelve `501`: Graph, OBO y credenciales siguen pendientes por diseño.

## Tracking de video (Fase 7)

El reproductor registra solamente intervalos de avance normal y envía checkpoints al pausar, terminar, ocultar/salir de la página y cada 30 segundos. `POST /api/lessons/{id}/progress` valida duración y rangos, consolida solapamientos, conserva `last_position_seconds` para reanudar y marca la lección cuando supera su `completion_threshold`.

## Dashboard (Fase 8)

`GET /api/dashboard` y la portada muestran el contenido disponible para el usuario actual, progreso general, lecciones para continuar, cursos recientes y completados. `/mi-aprendizaje` concentra los cursos en progreso y terminados.

## Pruebas automatizadas

Las pruebas del backend usan una base SQLite aislada en memoria: no modifican la base PostgreSQL local ni el catálogo demo.

```bash
cd backend
.venv/bin/python -m pytest -q
```

La configuración se toma de variables de entorno. Consulte `backend/.env.example` y `frontend/.env.example`; no incluya secretos en el repositorio.
