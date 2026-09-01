"""Business authorization for the learning catalog.

SharePoint authorizes the underlying organization storage.  This service is the
application-level gate that decides which Academy BID content a learner may
discover or request.
"""

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Module
from app.models.enums import ProgressStatus, Role
from app.models.progress import AcademyAssignment, CourseCompletion, CoursePrerequisite, Enrollment, LearningPathAssignment, ModuleAssignment
from app.providers.auth.base import AuthenticatedUser


def _is_admin(user: AuthenticatedUser) -> bool:
    return user.role == Role.ADMIN


def _has_assignments(session: Session, model, target_field: str, target_id: object) -> bool:
    return session.scalar(select(model.id).where(getattr(model, target_field) == target_id).limit(1)) is not None


def _has_user_assignment(session: Session, model, target_field: str, target_id: object, user_id: object) -> bool:
    return session.scalar(
        select(model.id).where(getattr(model, target_field) == target_id, model.user_id == user_id).limit(1)
    ) is not None


def group_allowed(groups: Iterable[object], user: AuthenticatedUser) -> bool:
    if _is_admin(user):
        return True
    user_group_ids = {group_id for group_id, _ in user.groups}
    return not groups or any(group.id in user_group_ids for group in groups)


def academy_allowed(session: Session, academy: Academy, user: AuthenticatedUser) -> bool:
    if _is_admin(user):
        return True
    if _has_assignments(session, AcademyAssignment, "academy_id", academy.id):
        return _has_user_assignment(session, AcademyAssignment, "academy_id", academy.id, user.id)
    return group_allowed(academy.groups, user)


def path_allowed(session: Session, path: LearningPath, user: AuthenticatedUser) -> bool:
    if _is_admin(user):
        return True
    if _has_assignments(session, LearningPathAssignment, "learning_path_id", path.id):
        return _has_user_assignment(session, LearningPathAssignment, "learning_path_id", path.id, user.id)
    return academy_allowed(session, path.academy, user)


def course_allowed_in_path(session: Session, course: Course, path: LearningPath, user: AuthenticatedUser) -> bool:
    if _is_admin(user):
        return True
    if _has_assignments(session, Enrollment, "course_id", course.id):
        return _has_user_assignment(session, Enrollment, "course_id", course.id, user.id)
    if session.scalar(select(ModuleAssignment.id).join(Module).where(Module.course_id == course.id, ModuleAssignment.user_id == user.id).limit(1)) is not None:
        return True
    return path_allowed(session, path, user) and group_allowed(course.groups, user)


def course_allowed(session: Session, course: Course, user: AuthenticatedUser) -> bool:
    if _is_admin(user):
        return True
    paths = session.scalars(
        select(LearningPath).join(LearningPathCourse).where(LearningPathCourse.course_id == course.id)
    ).all()
    return any(course_allowed_in_path(session, course, path, user) for path in paths)


def module_allowed(session: Session, module: Module, user: AuthenticatedUser) -> bool:
    if _is_admin(user):
        return True
    if _has_assignments(session, ModuleAssignment, "module_id", module.id):
        return _has_user_assignment(session, ModuleAssignment, "module_id", module.id, user.id)
    return course_allowed(session, module.course, user)


def course_unlocked(session: Session, course: Course, user: AuthenticatedUser) -> bool:
    """Return whether all required courses were completed by this learner."""
    if _is_admin(user):
        return True
    prerequisite_ids = session.scalars(
        select(CourseCompletion.course_id)
        .join_from(CourseCompletion, CoursePrerequisite, CourseCompletion.course_id == CoursePrerequisite.prerequisite_course_id)
        .where(
            CoursePrerequisite.course_id == course.id,
            CourseCompletion.user_id == user.id,
            CourseCompletion.status == ProgressStatus.COMPLETED,
        )
    ).all()
    required_ids = session.scalars(
        select(CoursePrerequisite.prerequisite_course_id).where(
            CoursePrerequisite.course_id == course.id
        )
    ).all()
    return set(required_ids).issubset(set(prerequisite_ids))
