from app.models.enums import ProgressStatus, Role
from app.models.identity import User
from app.models.progress import AcademyAssignment, CourseCompletion, CoursePrerequisite, Enrollment
from app.providers.auth.base import AuthenticatedUser
from app.services.access import academy_allowed, course_allowed, course_unlocked
from conftest import make_authenticated_user


def test_course_assignment_restricts_course_to_selected_user(db_session, sample_lesson):
    selected = User(external_id="selected", name="Selected", email="selected@example.test", role=Role.LEARNER)
    unassigned = User(external_id="unassigned", name="Unassigned", email="unassigned@example.test", role=Role.LEARNER)
    db_session.add_all([selected, unassigned]); db_session.flush()
    db_session.add(Enrollment(user_id=selected.id, course_id=sample_lesson.course.id))
    db_session.commit()

    selected_user = AuthenticatedUser(id=selected.id, external_id=selected.external_id, name=selected.name, email=selected.email, role=Role.LEARNER, groups=())
    unassigned_user = AuthenticatedUser(id=unassigned.id, external_id=unassigned.external_id, name=unassigned.name, email=unassigned.email, role=Role.LEARNER, groups=())
    assert course_allowed(db_session, sample_lesson.course, selected_user)
    assert not course_allowed(db_session, sample_lesson.course, unassigned_user)


def test_academy_assignment_restricts_academy_to_selected_user(db_session, sample_lesson):
    academy = sample_lesson.course.learning_path_links[0].learning_path.academy
    selected = User(external_id="academy-selected", name="Academy Selected", email="academy-selected@example.test", role=Role.LEARNER)
    unassigned = User(external_id="academy-unassigned", name="Academy Unassigned", email="academy-unassigned@example.test", role=Role.LEARNER)
    db_session.add_all([selected, unassigned]); db_session.flush()
    db_session.add(AcademyAssignment(user_id=selected.id, academy_id=academy.id))
    db_session.commit()

    selected_user = AuthenticatedUser(id=selected.id, external_id=selected.external_id, name=selected.name, email=selected.email, role=Role.LEARNER, groups=())
    unassigned_user = AuthenticatedUser(id=unassigned.id, external_id=unassigned.external_id, name=unassigned.name, email=unassigned.email, role=Role.LEARNER, groups=())
    assert academy_allowed(db_session, academy, selected_user)
    assert not academy_allowed(db_session, academy, unassigned_user)


def test_prerequisite_requires_completed_course(db_session, sample_lesson):
    from app.models.catalog import Course

    advanced = Course(title="Advanced", slug="advanced", is_published=True)
    db_session.add(advanced); db_session.flush()
    db_session.add(CoursePrerequisite(course_id=advanced.id, prerequisite_course_id=sample_lesson.course.id))
    db_session.commit()

    assert not course_unlocked(db_session, advanced, sample_lesson.user)
    db_session.add(CourseCompletion(user_id=sample_lesson.user.id, course_id=sample_lesson.course.id, status=ProgressStatus.COMPLETED, progress_percent=100))
    db_session.commit()
    assert course_unlocked(db_session, advanced, sample_lesson.user)


def test_admin_can_manage_assignments_and_prerequisites(client, sample_lesson):
    test_client, set_current_user = client
    admin = AuthenticatedUser(
        id=sample_lesson.user.id,
        external_id=sample_lesson.user.external_id,
        name=sample_lesson.user.name,
        email=sample_lesson.user.email,
        role=Role.ADMIN,
        groups=(),
    )
    set_current_user(admin)
    overview = test_client.get("/api/admin/overview")
    assert overview.status_code == 200
    assert overview.json()["users"][0]["id"] == str(sample_lesson.user.id)

    academy_id = sample_lesson.course.learning_path_links[0].learning_path.academy_id
    assigned = test_client.post("/api/admin/assignments", json={"user_id": str(sample_lesson.user.id), "target_type": "ACADEMY", "target_id": str(academy_id)})
    assert assigned.status_code == 201
    assert len(test_client.get("/api/admin/assignments").json()) == 2

    prerequisite = test_client.post("/api/admin/prerequisites", json={"course_id": str(sample_lesson.course.id), "prerequisite_course_id": str(sample_lesson.course.id)})
    assert prerequisite.status_code == 422


def test_catalog_only_returns_content_with_a_direct_assignment(client, sample_lesson):
    test_client, set_current_user = client
    assigned_catalog = test_client.get("/api/academies")
    assert assigned_catalog.status_code == 200
    assert len(assigned_catalog.json()) == 1

    set_current_user(make_authenticated_user(Role.LEARNER))
    unassigned_catalog = test_client.get("/api/academies")
    assert unassigned_catalog.status_code == 200
    assert unassigned_catalog.json() == []
