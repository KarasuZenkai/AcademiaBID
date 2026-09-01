from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.providers.auth.base import AuthenticatedUser
from app.services.graph import GraphService
from app.services.sharepoint_sync import sync_user_catalog
from app.db.session import get_db_session

router = APIRouter(prefix="/api/sharepoint", tags=["sharepoint"])


@router.get("/connection")
def connection(user: AuthenticatedUser = Depends(get_current_user)):
    if not user.access_token:
        return {"mode": "local", "message": "Microsoft Entra authentication is required for SharePoint live access."}
    return GraphService().inspect_site(user.access_token)


@router.get("/drives/{drive_id}/items/{item_id}/children")
def children(drive_id: str, item_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    return GraphService().list_children(drive_id, item_id, user.access_token or "")


@router.post("/sync")
def sync(session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)):
    if not user.access_token:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Microsoft Entra authentication is required")
    return sync_user_catalog(session, user)


@router.post("/drives/{drive_id}/items/{item_id}/playback")
def playback(drive_id: str, item_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    return {"url": GraphService().playback_url(drive_id, item_id, user.access_token or "")}
