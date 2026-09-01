import logging
from typing import Optional

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models.enums import Role
from app.models.identity import User
from app.providers.auth.base import AuthenticatedUser

logger = logging.getLogger(__name__)


class EntraCurrentUserProvider:
    """Validate a token minted for this API and map its user to local progress."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_current_user(self, development_user_id: Optional[str], authorization: Optional[str] = None) -> AuthenticatedUser:
        settings = get_settings()
        if not settings.azure_tenant_id or not settings.azure_backend_client_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Microsoft Entra configuration is incomplete")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

        access_token = authorization.removeprefix("Bearer ").strip()
        try:
            issuers = [
                f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0",
                f"https://sts.windows.net/{settings.azure_tenant_id}/",
            ]
            signing_key = PyJWKClient(f"https://login.microsoftonline.com/{settings.azure_tenant_id}/discovery/v2.0/keys").get_signing_key_from_jwt(access_token)
            claims = jwt.decode(
                access_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=[settings.azure_backend_client_id, f"api://{settings.azure_backend_client_id}"],
                issuer=issuers,
            )
        except jwt.PyJWTError as error:
            logger.warning("Microsoft Entra token validation failed: %s", error)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Microsoft Entra access token") from error

        external_id = claims.get("oid")
        email = claims.get("preferred_username") or claims.get("upn")
        name = claims.get("name") or email
        if not external_id or not email or not name:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Microsoft Entra token is missing required user claims")

        user = self.session.scalar(select(User).options(selectinload(User.groups)).where(User.external_id == external_id))
        if user is None:
            user = User(external_id=external_id, email=email, name=name, role=Role.LEARNER)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        elif not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        else:
            user.email = email
            user.name = name
            self.session.commit()

        return AuthenticatedUser(
            id=user.id,
            external_id=user.external_id,
            name=user.name,
            email=user.email,
            role=user.role,
            groups=tuple(sorted(((group.id, group.name) for group in user.groups), key=lambda group: group[1])),
            access_token=access_token,
        )
