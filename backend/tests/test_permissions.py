from app.models.identity import Group
from app.models.enums import Role

from conftest import make_authenticated_user


def test_restricted_lesson_is_hidden_from_users_outside_its_group(client, db_session, sample_lesson) -> None:
    test_client, _ = client
    group = Group(name="Tecnología")
    sample_lesson.course.groups.append(group)
    db_session.commit()

    response = test_client.get(f"/api/lessons/{sample_lesson.lesson.id}")

    assert response.status_code == 404


def test_admin_endpoints_require_the_admin_role(client, sample_lesson) -> None:
    test_client, set_current_user = client

    denied = test_client.get("/api/admin/overview")
    assert denied.status_code == 403

    set_current_user(make_authenticated_user(Role.ADMIN))
    allowed = test_client.get("/api/admin/overview")
    assert allowed.status_code == 200
    assert len(allowed.json()["academies"]) == 1


def test_compliance_dashboard_requires_the_admin_role(client, sample_lesson) -> None:
    test_client, set_current_user = client

    assert test_client.get("/api/cumplimiento").status_code == 403

    set_current_user(make_authenticated_user(Role.ADMIN))
    response = test_client.get("/api/cumplimiento")
    assert response.status_code == 200
    assert response.json()["summary"]["unit_count"] == 1


def test_profile_photo_falls_back_cleanly_when_not_using_entra(client) -> None:
    test_client, _ = client

    response = test_client.get("/api/me/photo")

    assert response.status_code == 204


def test_profile_details_fall_back_cleanly_when_not_using_entra(client) -> None:
    test_client, _ = client

    response = test_client.get("/api/me/profile")

    assert response.status_code == 200
    assert response.json() == {"job_title": None, "company_name": None}
