from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.db.session import database_is_available

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    database: str


@router.get("/health", response_model=HealthResponse)
def health(response: Response) -> HealthResponse:
    """Readiness endpoint that only reports healthy after PostgreSQL responds."""
    if database_is_available():
        return HealthResponse(status="ok", database="connected")

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status="unavailable", database="unavailable")
