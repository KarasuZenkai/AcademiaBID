from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin
from app.models.enums import LessonType

if TYPE_CHECKING:
    from app.models.identity import Group
    from app.models.progress import AcademyAssignment, CourseCompletion, CoursePrerequisite, Enrollment, LearningPathAssignment, LearningPathCompletion, LessonProgress, ModuleAssignment, QuizAttempt, VideoRange, VideoSession

academy_groups = Table("academy_groups", Base.metadata,
    Column("academy_id", ForeignKey("academies.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True))
course_groups = Table("course_groups", Base.metadata,
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True))


class Academy(UUIDTimestampMixin, Base):
    __tablename__ = "academies"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(2048))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    groups: Mapped[list[Group]] = relationship(secondary=academy_groups, back_populates="academies")
    learning_paths: Mapped[list[LearningPath]] = relationship(back_populates="academy", cascade="all, delete-orphan")
    assignments: Mapped[list[AcademyAssignment]] = relationship(back_populates="academy", cascade="all, delete-orphan")


class LearningPath(UUIDTimestampMixin, Base):
    __tablename__ = "learning_paths"
    __table_args__ = (UniqueConstraint("academy_id", "position", name="uq_learning_path_academy_position"),)
    academy_id: Mapped[object] = mapped_column(ForeignKey("academies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    academy: Mapped[Academy] = relationship(back_populates="learning_paths")
    course_links: Mapped[list[LearningPathCourse]] = relationship(back_populates="learning_path", cascade="all, delete-orphan")
    completions: Mapped[list[LearningPathCompletion]] = relationship(back_populates="learning_path", cascade="all, delete-orphan")
    assignments: Mapped[list[LearningPathAssignment]] = relationship(back_populates="learning_path", cascade="all, delete-orphan")


class Course(UUIDTimestampMixin, Base):
    __tablename__ = "courses"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(2048))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    groups: Mapped[list[Group]] = relationship(secondary=course_groups, back_populates="courses")
    learning_path_links: Mapped[list[LearningPathCourse]] = relationship(back_populates="course", cascade="all, delete-orphan")
    modules: Mapped[list[Module]] = relationship(back_populates="course", cascade="all, delete-orphan")
    enrollments: Mapped[list[Enrollment]] = relationship(back_populates="course", cascade="all, delete-orphan")
    completions: Mapped[list[CourseCompletion]] = relationship(back_populates="course", cascade="all, delete-orphan")
    prerequisites: Mapped[list[CoursePrerequisite]] = relationship(
        foreign_keys="CoursePrerequisite.course_id", back_populates="course", cascade="all, delete-orphan"
    )
    required_for: Mapped[list[CoursePrerequisite]] = relationship(
        foreign_keys="CoursePrerequisite.prerequisite_course_id", back_populates="prerequisite_course", cascade="all, delete-orphan"
    )


class LearningPathCourse(Base):
    __tablename__ = "learning_path_courses"
    __table_args__ = (UniqueConstraint("learning_path_id", "position", name="uq_learning_path_course_position"),)
    learning_path_id: Mapped[object] = mapped_column(ForeignKey("learning_paths.id", ondelete="CASCADE"), primary_key=True)
    course_id: Mapped[object] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    learning_path: Mapped[LearningPath] = relationship(back_populates="course_links")
    course: Mapped[Course] = relationship(back_populates="learning_path_links")


class Module(UUIDTimestampMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_module_course_position"),)
    course_id: Mapped[object] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    course: Mapped[Course] = relationship(back_populates="modules")
    lessons: Mapped[list[Lesson]] = relationship(back_populates="module", cascade="all, delete-orphan")
    assignments: Mapped[list[ModuleAssignment]] = relationship(back_populates="module", cascade="all, delete-orphan")


class Lesson(UUIDTimestampMixin, Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("module_id", "position", name="uq_lesson_module_position"), CheckConstraint("completion_threshold >= 0 AND completion_threshold <= 1", name="ck_lesson_completion_threshold"), CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0", name="ck_lesson_duration_seconds"))
    module_id: Mapped[object] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    lesson_type: Mapped[LessonType] = mapped_column(SAEnum(LessonType, name="lesson_type"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    completion_threshold: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.9000"), nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    sharepoint_site_id: Mapped[Optional[str]] = mapped_column(String(512))
    sharepoint_drive_id: Mapped[Optional[str]] = mapped_column(String(512))
    sharepoint_item_id: Mapped[Optional[str]] = mapped_column(String(512))
    document_url: Mapped[Optional[str]] = mapped_column(String(2048))
    external_url: Mapped[Optional[str]] = mapped_column(String(2048))
    module: Mapped[Module] = relationship(back_populates="lessons")
    progress_records: Mapped[list[LessonProgress]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    video_sessions: Mapped[list[VideoSession]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    video_ranges: Mapped[list[VideoRange]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list[QuizAttempt]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
