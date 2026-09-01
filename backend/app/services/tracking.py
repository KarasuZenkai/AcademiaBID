import uuid
from decimal import Decimal
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.catalog import Course, LearningPathCourse, Lesson, Module
from app.models.common import utcnow
from app.models.enums import ProgressStatus
from app.models.progress import CourseCompletion, LearningPathCompletion, LessonProgress, VideoRange

Range = Tuple[int, int]


def merge_ranges(ranges: Iterable[Range]) -> List[Range]:
    ordered = sorted(ranges)
    merged: List[Range] = []
    for start, end in ordered:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def watched_seconds(ranges: Iterable[Range]) -> int:
    return sum(end - start for start, end in merge_ranges(ranges))


def update_course_completion(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> float:
    session.flush()
    required_lessons = session.scalars(select(Lesson).join(Module).where(Module.course_id == course_id, Lesson.is_required.is_(True))).all()
    completed = 0
    if required_lessons:
        lesson_ids = [lesson.id for lesson in required_lessons]
        completed = session.scalar(select(func.count()).select_from(LessonProgress).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id.in_(lesson_ids), LessonProgress.status == ProgressStatus.COMPLETED)) or 0
    percentage = (completed / len(required_lessons) * 100) if required_lessons else 0
    record = session.scalar(select(CourseCompletion).where(CourseCompletion.user_id == user_id, CourseCompletion.course_id == course_id))
    if record is None:
        record = CourseCompletion(user_id=user_id, course_id=course_id)
        session.add(record)
    record.progress_percent = Decimal(str(round(percentage, 2)))
    record.status = ProgressStatus.COMPLETED if required_lessons and completed == len(required_lessons) else ProgressStatus.IN_PROGRESS if completed else ProgressStatus.NOT_STARTED
    record.completed_at = utcnow() if record.status == ProgressStatus.COMPLETED else None
    update_learning_path_completions(session, user_id, course_id)
    return percentage


def update_learning_path_completions(session: Session, user_id: uuid.UUID, course_id: uuid.UUID) -> None:
    links = session.scalars(select(LearningPathCourse).where(LearningPathCourse.course_id == course_id)).all()
    for link in links:
        required = session.scalars(select(LearningPathCourse).where(LearningPathCourse.learning_path_id == link.learning_path_id, LearningPathCourse.is_required.is_(True))).all()
        completed = 0
        for required_link in required:
            record = session.scalar(select(CourseCompletion).where(CourseCompletion.user_id == user_id, CourseCompletion.course_id == required_link.course_id))
            if record and record.status == ProgressStatus.COMPLETED: completed += 1
        percentage = completed / len(required) * 100 if required else 0
        path_record = session.scalar(select(LearningPathCompletion).where(LearningPathCompletion.user_id == user_id, LearningPathCompletion.learning_path_id == link.learning_path_id))
        if path_record is None:
            path_record = LearningPathCompletion(user_id=user_id, learning_path_id=link.learning_path_id)
            session.add(path_record)
        path_record.progress_percent = Decimal(str(round(percentage, 2)))
        path_record.status = ProgressStatus.COMPLETED if required and completed == len(required) else ProgressStatus.IN_PROGRESS if completed else ProgressStatus.NOT_STARTED
        path_record.completed_at = utcnow() if path_record.status == ProgressStatus.COMPLETED else None


def apply_video_progress(session: Session, user_id: uuid.UUID, lesson: Lesson, position: float, duration: float, new_ranges: Iterable[Range], session_id: Optional[uuid.UUID]) -> tuple[LessonProgress, float]:
    effective_duration = lesson.duration_seconds or int(duration)
    # SharePoint and the browser can report slightly different container durations.
    # When the lesson has synchronized metadata, it is the authoritative bound for
    # ranges and percentages; the browser value is only a fallback for local media.
    if position > effective_duration + 5:
        raise ValueError("Position exceeds the lesson duration")
    validated = []
    for start, end in new_ranges:
        if start < 0 or end <= start or end > effective_duration + 5:
            raise ValueError("Invalid watched range")
        validated.append((start, min(end, effective_duration)))
    existing = session.scalars(select(VideoRange).where(VideoRange.user_id == user_id, VideoRange.lesson_id == lesson.id)).all()
    merged = merge_ranges([(item.start_seconds, item.end_seconds) for item in existing] + validated)
    for item in existing: session.delete(item)
    for start, end in merged: session.add(VideoRange(user_id=user_id, lesson_id=lesson.id, video_session_id=None, start_seconds=start, end_seconds=end))
    progress = session.scalar(select(LessonProgress).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson.id))
    if progress is None:
        progress = LessonProgress(user_id=user_id, lesson_id=lesson.id)
        session.add(progress)
    progress.watched_seconds = watched_seconds(merged)
    progress.last_position_seconds = min(int(position), effective_duration)
    percentage = min(progress.watched_seconds / effective_duration * 100, 100)
    if percentage >= float(lesson.completion_threshold) * 100:
        progress.status = ProgressStatus.COMPLETED; progress.completed_at = utcnow()
    elif progress.watched_seconds:
        progress.status = ProgressStatus.IN_PROGRESS; progress.completed_at = None
    return progress, percentage
