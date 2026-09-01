from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.catalog import router as catalog_router
from app.api.routes.admin import router as admin_router
from app.api.routes.lessons import router as lessons_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.achievements import router as achievements_router
from app.api.routes.sharepoint import router as sharepoint_router
from app.api.routes.compliance import router as compliance_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Academia BID API",
    version="0.1.0",
    description="Backend REST local para Academia BID.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Dev-User-Id"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(admin_router)
app.include_router(lessons_router)
app.include_router(dashboard_router)
app.include_router(achievements_router)
app.include_router(sharepoint_router)
app.include_router(compliance_router)
app.mount("/media", StaticFiles(directory=Path(__file__).resolve().parents[1] / "media"), name="media")
