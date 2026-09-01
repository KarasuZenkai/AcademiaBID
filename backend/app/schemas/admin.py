import uuid
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import LessonType


class AcademyWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255); slug: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None; image_url: Optional[str] = None; is_published: bool = False


class PathWrite(BaseModel):
    academy_id: uuid.UUID; name: str; slug: str; description: Optional[str] = None; position: int = Field(ge=0); is_published: bool = False


class CourseWrite(BaseModel):
    title: str; slug: str; description: Optional[str] = None; thumbnail_url: Optional[str] = None; estimated_minutes: Optional[int] = Field(default=None, ge=0); is_published: bool = False


class PathCourseWrite(BaseModel):
    course_id: uuid.UUID; position: int = Field(ge=0); is_required: bool = True


class ModuleWrite(BaseModel):
    course_id: uuid.UUID; title: str; description: Optional[str] = None; position: int = Field(ge=0)


class LessonWrite(BaseModel):
    module_id: uuid.UUID; title: str; description: Optional[str] = None; lesson_type: LessonType; position: int = Field(ge=0)
    is_required: bool = True; completion_threshold: Decimal = Field(default=Decimal("0.9"), ge=0, le=1); duration_seconds: Optional[int] = Field(default=None, ge=0)
    sharepoint_site_id: Optional[str] = None; sharepoint_drive_id: Optional[str] = None; sharepoint_item_id: Optional[str] = None; document_url: Optional[str] = None; external_url: Optional[str] = None


class AssignmentTarget(str, Enum):
    ACADEMY = "ACADEMY"
    LEARNING_PATH = "LEARNING_PATH"
    COURSE = "COURSE"
    MODULE = "MODULE"


class AssignmentWrite(BaseModel):
    user_id: uuid.UUID
    target_type: AssignmentTarget
    target_id: uuid.UUID


class PrerequisiteWrite(BaseModel):
    course_id: uuid.UUID
    prerequisite_course_id: uuid.UUID
