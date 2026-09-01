from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Enum as SAEnum, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin
from app.models.enums import Role

if TYPE_CHECKING:
    from app.models.catalog import Academy, Course
    from app.models.progress import AcademyAssignment, AuditLog, CourseCompletion, Enrollment, LearningPathAssignment, LearningPathCompletion, LessonProgress, ModuleAssignment, QuizAttempt, VideoRange, VideoSession

user_groups = Table(
    "user_groups", Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class User(UUIDTimestampMixin, Base):
    __tablename__ = "users"
    external_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    role: Mapped[Role] = mapped_column(SAEnum(Role, name="role"), default=Role.LEARNER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    groups: Mapped[list[Group]] = relationship(secondary=user_groups, back_populates="users")
    enrollments: Mapped[list[Enrollment]] = relationship(back_populates="user", cascade="all, delete-orphan")
    lesson_progress: Mapped[list[LessonProgress]] = relationship(back_populates="user", cascade="all, delete-orphan")
    video_sessions: Mapped[list[VideoSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
    video_ranges: Mapped[list[VideoRange]] = relationship(back_populates="user", cascade="all, delete-orphan")
    course_completions: Mapped[list[CourseCompletion]] = relationship(back_populates="user", cascade="all, delete-orphan")
    learning_path_completions: Mapped[list[LearningPathCompletion]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list[QuizAttempt]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="actor")
    academy_assignments: Mapped[list[AcademyAssignment]] = relationship(back_populates="user", cascade="all, delete-orphan")
    learning_path_assignments: Mapped[list[LearningPathAssignment]] = relationship(back_populates="user", cascade="all, delete-orphan")
    module_assignments: Mapped[list[ModuleAssignment]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Group(UUIDTimestampMixin, Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    users: Mapped[list[User]] = relationship(secondary=user_groups, back_populates="groups")
    academies: Mapped[list[Academy]] = relationship(secondary="academy_groups", back_populates="groups")
    courses: Mapped[list[Course]] = relationship(secondary="course_groups", back_populates="groups")
