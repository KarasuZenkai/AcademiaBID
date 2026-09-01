from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin, utcnow
from app.models.enums import ProgressStatus

if TYPE_CHECKING:
    from app.models.catalog import Course, LearningPath, Lesson
    from app.models.identity import User


class Enrollment(UUIDTimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    user: Mapped[User] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship(back_populates="enrollments")


class LessonProgress(UUIDTimestampMixin, Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"), CheckConstraint("watched_seconds >= 0", name="ck_lesson_progress_watched_seconds"), CheckConstraint("last_position_seconds >= 0", name="ck_lesson_progress_last_position"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(SAEnum(ProgressStatus, name="progress_status"), default=ProgressStatus.NOT_STARTED, nullable=False)
    watched_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_position_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="lesson_progress")
    lesson: Mapped[Lesson] = relationship(back_populates="progress_records")


class VideoSession(UUIDTimestampMixin, Base):
    __tablename__ = "video_sessions"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="video_sessions")
    lesson: Mapped[Lesson] = relationship(back_populates="video_sessions")
    ranges: Mapped[list[VideoRange]] = relationship(back_populates="video_session", cascade="all, delete-orphan")


class VideoRange(UUIDTimestampMixin, Base):
    __tablename__ = "video_ranges"
    __table_args__ = (CheckConstraint("start_seconds >= 0", name="ck_video_range_start_seconds"), CheckConstraint("end_seconds > start_seconds", name="ck_video_range_end_after_start"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    video_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("video_sessions.id", ondelete="SET NULL"))
    start_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    end_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    user: Mapped[User] = relationship(back_populates="video_ranges")
    lesson: Mapped[Lesson] = relationship(back_populates="video_ranges")
    video_session: Mapped[Optional[VideoSession]] = relationship(back_populates="ranges")


class CourseCompletion(UUIDTimestampMixin, Base):
    __tablename__ = "course_completion"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_course_completion_user_course"),)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(SAEnum(ProgressStatus, name="progress_status", create_type=False), default=ProgressStatus.NOT_STARTED, nullable=False)
    progress_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="course_completions")
    course: Mapped[Course] = relationship(back_populates="completions")


class LearningPathCompletion(UUIDTimestampMixin, Base):
    __tablename__ = "learning_path_completion"
    __table_args__ = (UniqueConstraint("user_id", "learning_path_id", name="uq_learning_path_completion_user_path"),)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_path_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(SAEnum(ProgressStatus, name="progress_status", create_type=False), default=ProgressStatus.NOT_STARTED, nullable=False)
    progress_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="learning_path_completions")
    learning_path: Mapped[LearningPath] = relationship(back_populates="completions")


class QuizAttempt(UUIDTimestampMixin, Base):
    __tablename__ = "quiz_attempts"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    answers: Mapped[Optional[dict]] = mapped_column(JSON)
    user: Mapped[User] = relationship(back_populates="quiz_attempts")
    lesson: Mapped[Lesson] = relationship(back_populates="quiz_attempts")


class AuditLog(UUIDTimestampMixin, Base):
    __tablename__ = "audit_logs"
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]]
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    actor: Mapped[Optional[User]] = relationship(back_populates="audit_logs")
