from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.identity import User
from app.providers.auth.base import AuthenticatedUser
from app.schemas.auth import CurrentUserRead, DevelopmentUserRead, GroupRead
from app.services.graph import GraphService

router = APIRouter(prefix="/api", tags=["auth"])


def serialize_current_user(user: AuthenticatedUser) -> CurrentUserRead:
    return CurrentUserRead(
        id=user.id, external_id=user.external_id, name=user.name, email=user.email,
        role=user.role, groups=[GroupRead(id=group_id, name=name) for group_id, name in user.groups],
    )


@router.get("/me", response_model=CurrentUserRead)
def me(user: AuthenticatedUser = Depends(get_current_user)) -> CurrentUserRead:
    return serialize_current_user(user)


@router.get("/me/profile")
def my_profile_details(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    if get_settings().auth_provider != "entra" or not user.access_token:
        return {"job_title": None, "company_name": None}
    return GraphService().profile_details(user.access_token)


@router.get("/me/photo", responses={204: {"description": "The user does not have a profile photo"}})
def my_photo(user: AuthenticatedUser = Depends(get_current_user)) -> Response:
    if get_settings().auth_provider != "entra" or not user.access_token:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    photo = GraphService().profile_photo(user.access_token)
    if photo is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    content, media_type = photo
    return Response(content=content, media_type=media_type, headers={"Cache-Control": "private, max-age=300"})


@router.get("/me/groups", response_model=list[GroupRead])
def my_groups(user: AuthenticatedUser = Depends(get_current_user)) -> list[GroupRead]:
    return serialize_current_user(user).groups


@router.get("/dev/users", response_model=list[DevelopmentUserRead], include_in_schema=False)
def development_users(session: Session = Depends(get_db_session)) -> list[DevelopmentUserRead]:
    if get_settings().auth_provider != "local":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    users = session.scalars(select(User).where(User.is_active.is_(True)).order_by(User.name)).all()
    return [DevelopmentUserRead(id=user.id, external_id=user.external_id or "", name=user.name, email=user.email, role=user.role) for user in users]
