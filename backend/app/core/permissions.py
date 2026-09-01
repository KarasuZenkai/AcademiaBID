from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.enums import Role
from app.providers.auth.base import AuthenticatedUser


def require_roles(*allowed_roles: Role) -> Callable:
    """Dependency factory for future admin and learner endpoints."""
    def verify(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return verify
