from app.core.config import get_settings
from app.providers.media.base import PlaybackSource


class LocalMediaProvider:
    """Development-only provider for the local MP4 fixture."""

    def get_playback_source(self, site_id, drive_id, item_id) -> PlaybackSource:
        return PlaybackSource(url=get_settings().local_media_url)
