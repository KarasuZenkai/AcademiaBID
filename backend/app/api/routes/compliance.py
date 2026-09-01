from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db_session
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse
from app.models.enums import ProgressStatus, Role
from app.models.identity import Group, User
from app.models.progress import CourseCompletion
from app.providers.auth.base import AuthenticatedUser

router = APIRouter(prefix="/api", tags=["compliance"])
leadership_only = Depends(require_roles(Role.ADMIN))


@router.get("/cumplimiento")
def compliance_dashboard(
    session: Session = Depends(get_db_session),
    _: AuthenticatedUser = leadership_only,
) -> dict:
    """Demo leadership reporting. Scope is global today; future scopes belong here."""
    academies = session.scalars(
        select(Academy)
        .options(
            selectinload(Academy.groups).selectinload(Group.users),
            selectinload(Academy.learning_paths)
            .selectinload(LearningPath.course_links)
            .selectinload(LearningPathCourse.course),
        )
        .where(Academy.is_published.is_(True))
        .order_by(Academy.name)
    ).all()
    learners = session.scalars(
        select(User).options(selectinload(User.groups)).where(User.is_active.is_(True), User.role == Role.LEARNER).order_by(User.name)
    ).all()

    courses_by_academy = {
        academy.id: [
            link.course
            for path in academy.learning_paths
            if path.is_published
            for link in path.course_links
            if link.course.is_published
        ]
        for academy in academies
    }
    course_ids = {course.id for courses in courses_by_academy.values() for course in courses}
    completions = session.scalars(select(CourseCompletion).where(CourseCompletion.course_id.in_(course_ids))).all() if course_ids else []
    progress = {(item.user_id, item.course_id): item for item in completions}

    unit_rows = []
    user_units = defaultdict(list)
    learner_rows = {}
    total_assignments = total_completed = 0
    for academy in academies:
        courses = courses_by_academy[academy.id]
        group_ids = {group.id for group in academy.groups}
        unit_learners = [learner for learner in learners if group_ids.intersection({group.id for group in learner.groups})]
        percentages = []
        completed_assignments = 0
        for learner in unit_learners:
            user_units[learner.id].append(academy.name)
            for course in courses:
                record = progress.get((learner.id, course.id))
                percentages.append(float(record.progress_percent) if record else 0)
                if record and record.status == ProgressStatus.COMPLETED:
                    completed_assignments += 1
        assignments = len(unit_learners) * len(courses)
        total_assignments += assignments
        total_completed += completed_assignments
        unit_rows.append({
            "name": academy.name,
            "slug": academy.slug,
            "assigned_users": len(unit_learners),
            "course_count": len(courses),
            "completed_assignments": completed_assignments,
            "pending_assignments": assignments - completed_assignments,
            "average_progress_percent": round(sum(percentages) / len(percentages), 2) if percentages else 0,
            "completion_rate_percent": round(completed_assignments / assignments * 100, 2) if assignments else 0,
        })

    for learner in learners:
        relevant_courses = [course for academy in academies if academy.name in user_units[learner.id] for course in courses_by_academy[academy.id]]
        records = [progress.get((learner.id, course.id)) for course in relevant_courses]
        learner_rows[learner.id] = {
            "name": learner.name,
            "units": user_units[learner.id],
            "average_progress_percent": round(sum(float(record.progress_percent) if record else 0 for record in records) / len(records), 2) if records else 0,
            "completed_courses": sum(record is not None and record.status == ProgressStatus.COMPLETED for record in records),
            "pending_courses": sum(record is None or record.status != ProgressStatus.COMPLETED for record in records),
        }

    unit_rows.sort(key=lambda item: item["completion_rate_percent"])
    users = sorted(learner_rows.values(), key=lambda item: (item["average_progress_percent"], item["name"]))
    return {
        "summary": {
            "assigned_users": len([learner for learner in learners if user_units[learner.id]]),
            "unit_count": len(academies),
            "completion_rate_percent": round(total_completed / total_assignments * 100, 2) if total_assignments else 0,
            "pending_assignments": total_assignments - total_completed,
        },
        "units": unit_rows,
        "users": users,
        "attention_units": unit_rows[:3],
    }
