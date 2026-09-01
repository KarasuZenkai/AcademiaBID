from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional, Protocol

from app.models.enums import Role


@dataclass(frozen=True)
class AuthenticatedUser:
    id: uuid.UUID
    external_id: Optional[str]
    name: str
    email: str
    role: Role
    groups: tuple[tuple[uuid.UUID, str], ...]
    access_token: Optional[str] = None


class CurrentUserProvider(Protocol):
    def get_current_user(self, development_user_id: Optional[str], authorization: Optional[str] = None) -> AuthenticatedUser:
        ...
