from fastapi import HTTPException, status
from app.core.config import get_settings
from app.providers.media.local import LocalMediaProvider
from app.providers.media.sharepoint import SharePointMediaProvider


def get_media_provider():
    provider = get_settings().media_provider
    if provider == "local": return LocalMediaProvider()
    if provider == "sharepoint": return SharePointMediaProvider()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unsupported media provider")
