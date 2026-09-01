"""Application-level authorization for assigned learning content only."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Module
from app.models.enums import ProgressStatus
from app.models.progress import AcademyAssignment, CourseCompletion, CoursePrerequisite, Enrollment, LearningPathAssignment, ModuleAssignment
from app.providers.auth.base import AuthenticatedUser


def _exists(session: Session, statement) -> bool:
    return session.scalar(statement.limit(1)) is not None


def _academy_granted(session: Session, academy_id: object, user_id: object) -> bool:
    return _exists(session, select(AcademyAssignment.id).where(AcademyAssignment.academy_id == academy_id, AcademyAssignment.user_id == user_id))


def _path_granted(session: Session, path_id: object, user_id: object) -> bool:
    return _exists(session, select(LearningPathAssignment.id).where(LearningPathAssignment.learning_path_id == path_id, LearningPathAssignment.user_id == user_id))


def _course_granted(session: Session, course_id: object, user_id: object) -> bool:
    return _exists(session, select(Enrollment.id).where(Enrollment.course_id == course_id, Enrollment.user_id == user_id))


def _module_granted(session: Session, module_id: object, user_id: object) -> bool:
    return _exists(session, select(ModuleAssignment.id).where(ModuleAssignment.module_id == module_id, ModuleAssignment.user_id == user_id))


def academy_allowed(session: Session, academy: Academy, user: AuthenticatedUser) -> bool:
    """An academy is visible when any assigned item belongs to it."""
    if _academy_granted(session, academy.id, user.id):
        return True
    if _exists(session, select(LearningPathAssignment.id).join(LearningPath).where(LearningPath.academy_id == academy.id, LearningPathAssignment.user_id == user.id)):
        return True
    if _exists(session, select(Enrollment.id).join(LearningPathCourse, Enrollment.course_id == LearningPathCourse.course_id).join(LearningPath).where(LearningPath.academy_id == academy.id, Enrollment.user_id == user.id)):
        return True
    return _exists(session, select(ModuleAssignment.id).join(Module).join(LearningPathCourse, Module.course_id == LearningPathCourse.course_id).join(LearningPath).where(LearningPath.academy_id == academy.id, ModuleAssignment.user_id == user.id))


def path_allowed(session: Session, path: LearningPath, user: AuthenticatedUser) -> bool:
    if _academy_granted(session, path.academy_id, user.id) or _path_granted(session, path.id, user.id):
        return True
    if _exists(session, select(Enrollment.id).join(LearningPathCourse, Enrollment.course_id == LearningPathCourse.course_id).where(LearningPathCourse.learning_path_id == path.id, Enrollment.user_id == user.id)):
        return True
    return _exists(session, select(ModuleAssignment.id).join(Module).join(LearningPathCourse, Module.course_id == LearningPathCourse.course_id).where(LearningPathCourse.learning_path_id == path.id, ModuleAssignment.user_id == user.id))


def course_allowed_in_path(session: Session, course: Course, path: LearningPath, user: AuthenticatedUser) -> bool:
    if _academy_granted(session, path.academy_id, user.id) or _path_granted(session, path.id, user.id) or _course_granted(session, course.id, user.id):
        return True
    return _exists(session, select(ModuleAssignment.id).join(Module).where(Module.course_id == course.id, ModuleAssignment.user_id == user.id))


def course_allowed(session: Session, course: Course, user: AuthenticatedUser) -> bool:
    paths = session.scalars(select(LearningPath).join(LearningPathCourse).where(LearningPathCourse.course_id == course.id)).all()
    return any(course_allowed_in_path(session, course, path, user) for path in paths)


def module_allowed(session: Session, module: Module, user: AuthenticatedUser) -> bool:
    if _module_granted(session, module.id, user.id):
        return True
    paths = session.scalars(select(LearningPath).join(LearningPathCourse).where(LearningPathCourse.course_id == module.course_id)).all()
    return any(_academy_granted(session, path.academy_id, user.id) or _path_granted(session, path.id, user.id) or _course_granted(session, module.course_id, user.id) for path in paths)


def course_unlocked(session: Session, course: Course, user: AuthenticatedUser) -> bool:
    """Return whether all required courses were completed by this learner."""
    completed_ids = session.scalars(
        select(CourseCompletion.course_id)
        .join_from(CourseCompletion, CoursePrerequisite, CourseCompletion.course_id == CoursePrerequisite.prerequisite_course_id)
        .where(CoursePrerequisite.course_id == course.id, CourseCompletion.user_id == user.id, CourseCompletion.status == ProgressStatus.COMPLETED)
    ).all()
    required_ids = session.scalars(select(CoursePrerequisite.prerequisite_course_id).where(CoursePrerequisite.course_id == course.id)).all()
    return set(required_ids).issubset(set(completed_ids))
