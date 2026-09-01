from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class PlaybackSource:
    url: str
    expires_at: Optional[str] = None


class MediaProvider(Protocol):
    def get_playback_source(self, site_id: Optional[str], drive_id: Optional[str], item_id: Optional[str]) -> PlaybackSource:
        ...
