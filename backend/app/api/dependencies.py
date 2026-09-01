from typing import Optional

from fastapi import Depends, Header
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.providers.auth.base import AuthenticatedUser
from app.providers.auth.factory import get_auth_provider


def get_current_user(
    x_dev_user_id: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
    session: Session = Depends(get_db_session),
) -> AuthenticatedUser:
    """Resolve the caller through the configured identity provider."""
    try:
        return get_auth_provider(session).get_current_user(x_dev_user_id, authorization)
    except NotImplementedError as error:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(error)) from error
