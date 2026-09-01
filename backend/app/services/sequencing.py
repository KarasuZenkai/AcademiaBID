from typing import Dict, Iterable, Optional, Set

from app.models.catalog import Course, Lesson
from app.models.enums import ProgressStatus
from app.models.progress import LessonProgress


def ordered_lessons(course: Course) -> list[Lesson]:
    return [
        lesson
        for module in sorted(course.modules, key=lambda item: item.position)
        for lesson in sorted(module.lessons, key=lambda item: item.position)
    ]


def unlocked_lesson_ids(course: Course, progress_records: Iterable[LessonProgress]) -> Set[object]:
    progress_by_lesson: Dict[object, LessonProgress] = {record.lesson_id: record for record in progress_records}
    unlocked: Set[object] = set()
    previous_required_complete = True
    for lesson in ordered_lessons(course):
        if previous_required_complete:
            unlocked.add(lesson.id)
        progress = progress_by_lesson.get(lesson.id)
        if lesson.is_required and (progress is None or progress.status != ProgressStatus.COMPLETED):
            previous_required_complete = False
    return unlocked


def next_lesson(course: Course, lesson_id: object) -> Optional[Lesson]:
    lessons = ordered_lessons(course)
    for index, lesson in enumerate(lessons):
        if lesson.id == lesson_id and index + 1 < len(lessons):
            return lessons[index + 1]
    return None
