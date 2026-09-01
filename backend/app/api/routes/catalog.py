from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Module
from app.models.enums import ProgressStatus
from app.models.progress import LessonProgress
from app.providers.auth.base import AuthenticatedUser
from app.services.sequencing import unlocked_lesson_ids

router = APIRouter(prefix="/api", tags=["catalog"])


def allows(groups, user: AuthenticatedUser) -> bool:
    return not groups or any(group.id in {group_id for group_id, _ in user.groups} for group in groups)


def academy_card(academy: Academy, user: Optional[AuthenticatedUser] = None) -> dict:
    paths = [path for path in academy.learning_paths if path.is_published] if "learning_paths" in academy.__dict__ else []
    courses = [link.course for path in paths for link in path.course_links if link.course.is_published and (user is None or allows(link.course.groups, user))]
    lessons = [lesson for course in courses for module in course.modules for lesson in module.lessons]
    return {"id": str(academy.id), "name": academy.name, "slug": academy.slug, "description": academy.description, "image_url": academy.image_url, "learning_path_count": len(paths), "content_count": len(lessons), "video_count": sum(lesson.lesson_type.value == "VIDEO" for lesson in lessons)}


@router.get("/academies")
def academies(session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> list[dict]:
    records = session.scalars(select(Academy).options(selectinload(Academy.groups), selectinload(Academy.learning_paths).selectinload(LearningPath.course_links).selectinload(LearningPathCourse.course).selectinload(Course.groups), selectinload(Academy.learning_paths).selectinload(LearningPath.course_links).selectinload(LearningPathCourse.course).selectinload(Course.modules).selectinload(Module.lessons)).where(Academy.is_published.is_(True)).order_by(Academy.name)).all()
    return [academy_card(academy, user) for academy in records if allows(academy.groups, user)]


@router.get("/academies/{slug}")
def academy_detail(slug: str, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    academy = session.scalar(select(Academy).options(selectinload(Academy.groups), selectinload(Academy.learning_paths).selectinload(LearningPath.course_links).selectinload(LearningPathCourse.course).selectinload(Course.groups), selectinload(Academy.learning_paths).selectinload(LearningPath.course_links).selectinload(LearningPathCourse.course).selectinload(Course.modules).selectinload(Module.lessons)).where(Academy.slug == slug, Academy.is_published.is_(True)))
    if academy is None or not allows(academy.groups, user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academy not found")
    paths = [path for path in academy.learning_paths if path.is_published]
    return {**academy_card(academy, user), "learning_paths": [{"name": path.name, "slug": path.slug, "description": path.description, "position": path.position, "course_count": len([link for link in path.course_links if link.course.is_published and allows(link.course.groups, user)]), "content_count": sum(len(module.lessons) for link in path.course_links if link.course.is_published and allows(link.course.groups, user) for module in link.course.modules)} for path in sorted(paths, key=lambda item: item.position)]}


@router.get("/rutas/{slug}")
def learning_path_detail(slug: str, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    path = session.scalar(select(LearningPath).options(selectinload(LearningPath.academy).selectinload(Academy.groups), selectinload(LearningPath.course_links).selectinload(LearningPathCourse.course).selectinload(Course.groups), selectinload(LearningPath.course_links).selectinload(LearningPathCourse.course).selectinload(Course.modules).selectinload(Module.lessons)).where(LearningPath.slug == slug, LearningPath.is_published.is_(True)))
    if path is None or not allows(path.academy.groups, user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")
    courses = [{"title": link.course.title, "slug": link.course.slug, "description": link.course.description, "estimated_minutes": link.course.estimated_minutes, "position": link.position, "content_count": sum(len(module.lessons) for module in link.course.modules), "video_count": sum(lesson.lesson_type.value == "VIDEO" for module in link.course.modules for lesson in module.lessons)} for link in sorted(path.course_links, key=lambda item: item.position) if link.course.is_published and allows(link.course.groups, user)]
    return {"name": path.name, "slug": path.slug, "description": path.description, "academy": academy_card(path.academy, user), "courses": courses}


@router.get("/cursos/{slug}")
def course_detail(slug: str, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    course = session.scalar(select(Course).options(selectinload(Course.groups), selectinload(Course.modules).selectinload(Module.lessons)).where(Course.slug == slug, Course.is_published.is_(True)))
    if course is None or not allows(course.groups, user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    lessons = [lesson for module in course.modules for lesson in module.lessons]
    progress_by_lesson = {}
    records = []
    if lessons:
        records = session.scalars(
            select(LessonProgress).where(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_id.in_([lesson.id for lesson in lessons]),
            )
        ).all()
        progress_by_lesson = {record.lesson_id: record for record in records}

    unlocked_ids = unlocked_lesson_ids(course, records)

    def lesson_card(lesson):
        progress = progress_by_lesson.get(lesson.id)
        watched_seconds = progress.watched_seconds if progress else 0
        return {
            "id": str(lesson.id),
            "title": lesson.title,
            "type": lesson.lesson_type.value,
            "position": lesson.position,
            "required": lesson.is_required,
            "progress_percent": round(watched_seconds / lesson.duration_seconds * 100, 2) if lesson.duration_seconds else 0,
            "resume_position_seconds": progress.last_position_seconds if progress else 0,
            "completed": bool(progress and progress.status == ProgressStatus.COMPLETED),
            "unlocked": lesson.id in unlocked_ids,
        }

    return {"title": course.title, "slug": course.slug, "description": course.description, "estimated_minutes": course.estimated_minutes, "modules": [{"title": module.title, "position": module.position, "lessons": [lesson_card(lesson) for lesson in sorted(module.lessons, key=lambda item: item.position)]} for module in sorted(course.modules, key=lambda item: item.position)]}
