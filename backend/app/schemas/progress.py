import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class WatchedRange(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(gt=0)


class ProgressWrite(BaseModel):
    position_seconds: float = Field(ge=0)
    duration_seconds: float = Field(gt=0)
    ranges: List[WatchedRange] = Field(default_factory=list, max_length=500)
    session_id: Optional[uuid.UUID] = None


class ProgressRead(BaseModel):
    watched_seconds: int
    progress_percent: float
    last_position_seconds: int
    completed: bool
    course_progress_percent: float
