from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.enums import ProgressStatus
from app.models.progress import CourseCompletion, LessonProgress
from app.providers.auth.base import AuthenticatedUser

from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api", tags=["dashboard"])

XP_PER_COMPLETED_COURSE = 100
XP_PER_LEVEL = 500


def allowed(groups, user: AuthenticatedUser) -> bool:
    user_group_ids = {group_id for group_id, _ in user.groups}
    return not groups or any(group.id in user_group_ids for group in groups)


@router.get("/dashboard")
def dashboard(session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    academies = session.scalars(select(Academy).options(selectinload(Academy.groups)).where(Academy.is_published.is_(True)).order_by(Academy.name)).all()
    available_academies = [academy for academy in academies if allowed(academy.groups, user)]
    links = session.scalars(select(LearningPathCourse).options(selectinload(LearningPathCourse.course).selectinload(Course.groups), selectinload(LearningPathCourse.learning_path).selectinload(LearningPath.academy).selectinload(Academy.groups))).all()
    available_courses = {}
    for link in links:
        if link.course.is_published and link.learning_path.is_published and link.learning_path.academy.is_published and allowed(link.course.groups, user) and allowed(link.learning_path.academy.groups, user):
            available_courses[link.course.id] = link.course
    course_ids = list(available_courses)
    completions = session.scalars(select(CourseCompletion).where(CourseCompletion.user_id == user.id, CourseCompletion.course_id.in_(course_ids)).order_by(CourseCompletion.completed_at.desc())).all() if course_ids else []
    completion_by_course = {item.course_id: item for item in completions}
    lesson_progress = session.scalars(select(LessonProgress).options(selectinload(LessonProgress.lesson).selectinload(Lesson.module).selectinload(Module.course)).where(LessonProgress.user_id == user.id, LessonProgress.status == ProgressStatus.IN_PROGRESS).order_by(LessonProgress.updated_at.desc())).all()
    continue_items = []
    for item in lesson_progress:
        course = item.lesson.module.course
        if course.id in available_courses:
            continue_items.append({"lesson_id": str(item.lesson.id), "lesson_title": item.lesson.title, "course_title": course.title, "course_slug": course.slug, "resume_position_seconds": item.last_position_seconds, "progress_percent": round(item.watched_seconds / item.lesson.duration_seconds * 100, 2) if item.lesson.duration_seconds else 0})
    completed = [{"title": available_courses[item.course_id].title, "slug": available_courses[item.course_id].slug, "completed_at": item.completed_at.isoformat() if item.completed_at else None} for item in completions if item.status == ProgressStatus.COMPLETED]
    total = len(course_ids)
    overall_progress = sum(float(completion_by_course[course_id].progress_percent) if course_id in completion_by_course else 0 for course_id in course_ids) / total if total else 0
    experience_points = len(completed) * XP_PER_COMPLETED_COURSE
    level = experience_points // XP_PER_LEVEL + 1
    return {"user_name": user.name, "overall_progress_percent": round(overall_progress, 2), "experience": {"points": experience_points, "level": level, "points_to_next_level": XP_PER_LEVEL - experience_points % XP_PER_LEVEL}, "badges": [{"title": item["title"], "course_slug": item["slug"], "awarded_at": item["completed_at"]} for item in completed[:5]], "continue_learning": continue_items[:5], "recent_courses": [{"title": course.title, "slug": course.slug, "progress_percent": float(completion_by_course[course.id].progress_percent) if course.id in completion_by_course else 0} for course in list(available_courses.values())[:6]], "completed_courses": completed[:6]}
