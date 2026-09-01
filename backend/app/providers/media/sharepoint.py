from app.providers.media.base import PlaybackSource


class SharePointMediaProvider:
    """Reserved for the Graph/OBO integration; deliberately not simulated."""

    def get_playback_source(self, site_id, drive_id, item_id) -> PlaybackSource:
        raise NotImplementedError("SharePoint playback requires a validated Microsoft Graph integration")
