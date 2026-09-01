from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.providers.auth.base import CurrentUserProvider
from app.providers.auth.entra import EntraCurrentUserProvider
from app.providers.auth.local import LocalCurrentUserProvider


def get_auth_provider(session: Session) -> CurrentUserProvider:
    settings = get_settings()
    if settings.auth_provider == "local":
        return LocalCurrentUserProvider(session, settings.local_default_user_id)
    if settings.auth_provider == "entra":
        return EntraCurrentUserProvider(session)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unsupported auth provider")
