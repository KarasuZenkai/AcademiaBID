import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.enums import Role


class GroupRead(BaseModel):
    id: uuid.UUID
    name: str


class CurrentUserRead(BaseModel):
    id: uuid.UUID
    external_id: Optional[str]
    name: str
    email: str
    role: Role
    groups: list[GroupRead]


class DevelopmentUserRead(BaseModel):
    id: uuid.UUID
    external_id: str
    name: str
    email: str
    role: Role
