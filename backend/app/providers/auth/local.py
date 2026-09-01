from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.identity import User
from app.providers.auth.base import AuthenticatedUser


class LocalCurrentUserProvider:
    """Development-only identity resolver backed by the seeded local users."""

    def __init__(self, session: Session, default_user_id: str) -> None:
        self.session = session
        self.default_user_id = default_user_id

    def get_current_user(self, development_user_id: Optional[str], authorization: Optional[str] = None) -> AuthenticatedUser:
        external_id = development_user_id or self.default_user_id
        user = self.session.scalar(
            select(User).options(selectinload(User.groups)).where(User.external_id == external_id, User.is_active.is_(True))
        )
        if user is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown local development user")
        return AuthenticatedUser(
            id=user.id,
            external_id=user.external_id,
            name=user.name,
            email=user.email,
            role=user.role,
            groups=tuple(sorted(((group.id, group.name) for group in user.groups), key=lambda group: group[1])),
        )
