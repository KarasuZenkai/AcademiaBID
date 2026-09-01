from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse
from app.models.enums import ProgressStatus
from app.models.progress import CourseCompletion
from app.providers.auth.base import AuthenticatedUser
from app.services.access import course_allowed_in_path

router = APIRouter(prefix="/api", tags=["achievements"])

XP_PER_COMPLETED_COURSE = 100
XP_PER_LEVEL = 500


@router.get("/logros")
def achievements(session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    links = session.scalars(select(LearningPathCourse).options(selectinload(LearningPathCourse.course).selectinload(Course.groups), selectinload(LearningPathCourse.learning_path).selectinload(LearningPath.academy).selectinload(Academy.groups))).all()
    available_courses = {link.course.id: link.course for link in links if link.course.is_published and link.learning_path.is_published and link.learning_path.academy.is_published and course_allowed_in_path(session, link.course, link.learning_path, user)}
    records = session.scalars(select(CourseCompletion).where(CourseCompletion.user_id == user.id, CourseCompletion.course_id.in_(list(available_courses)), CourseCompletion.status == ProgressStatus.COMPLETED).order_by(CourseCompletion.completed_at.desc())).all() if available_courses else []
    points = len(records) * XP_PER_COMPLETED_COURSE
    return {"experience": {"points": points, "level": points // XP_PER_LEVEL + 1, "points_to_next_level": XP_PER_LEVEL - points % XP_PER_LEVEL}, "badges": [{"title": available_courses[item.course_id].title, "awarded_at": item.completed_at.isoformat() if item.completed_at else None} for item in records]}
