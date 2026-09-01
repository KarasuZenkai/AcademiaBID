from app.services.tracking import merge_ranges, watched_seconds


def test_merge_ranges_and_watched_seconds() -> None:
    merged = merge_ranges([(0, 100), (80, 200), (190, 300), (900, 1200)])

    assert merged == [(0, 300), (900, 1200)]
    assert watched_seconds(merged) == 600


def test_progress_rejects_out_of_bounds_ranges(client, sample_lesson) -> None:
    test_client, _ = client

    response = test_client.post(
        f"/api/lessons/{sample_lesson.lesson.id}/progress",
        json={
            "position_seconds": 100,
            "duration_seconds": 100,
            "ranges": [{"start": 0, "end": 107}],
        },
    )

    assert response.status_code == 422


def test_progress_does_not_credit_a_skip_and_completes_at_threshold(client, sample_lesson) -> None:
    test_client, _ = client
    lesson_id = sample_lesson.lesson.id

    skipped = test_client.post(
        f"/api/lessons/{lesson_id}/progress",
        json={
            "position_seconds": 100,
            "duration_seconds": 100,
            "ranges": [{"start": 99, "end": 100}],
        },
    )
    assert skipped.status_code == 200
    assert skipped.json()["progress_percent"] == 1
    assert skipped.json()["completed"] is False

    completed = test_client.post(
        f"/api/lessons/{lesson_id}/progress",
        json={
            "position_seconds": 90,
            "duration_seconds": 100,
            "ranges": [{"start": 0, "end": 90}],
        },
    )
    assert completed.status_code == 200
    assert completed.json()["progress_percent"] == 91
    assert completed.json()["completed"] is True
    assert completed.json()["course_progress_percent"] == 100


def test_progress_uses_synced_duration_when_browser_reports_a_different_value(client, sample_lesson) -> None:
    test_client, _ = client

    response = test_client.post(
        f"/api/lessons/{sample_lesson.lesson.id}/progress",
        json={
            "position_seconds": 20,
            "duration_seconds": 120,
            "ranges": [{"start": 0, "end": 20}],
        },
    )

    assert response.status_code == 200
    assert response.json()["progress_percent"] == 20


def test_playback_resumes_from_the_saved_position(client, sample_lesson) -> None:
    test_client, _ = client
    lesson_id = sample_lesson.lesson.id
    progress = test_client.post(
        f"/api/lessons/{lesson_id}/progress",
        json={
            "position_seconds": 20,
            "duration_seconds": 100,
            "ranges": [{"start": 0, "end": 20}],
        },
    )
    assert progress.status_code == 200

    playback = test_client.post(f"/api/lessons/{lesson_id}/playback")

    assert playback.status_code == 200
    assert playback.json()["resume_position"] == 20
    assert playback.json()["session_id"]


def test_course_lists_the_viewing_state_for_each_lesson(client, sample_lesson) -> None:
    test_client, _ = client
    lesson_id = sample_lesson.lesson.id
    saved = test_client.post(
        f"/api/lessons/{lesson_id}/progress",
        json={"position_seconds": 90, "duration_seconds": 100, "ranges": [{"start": 0, "end": 90}]},
    )
    assert saved.status_code == 200

    course = test_client.get(f"/api/cursos/{sample_lesson.course.slug}")

    assert course.status_code == 200
    lesson = course.json()["modules"][0]["lessons"][0]
    assert lesson["completed"] is True
    assert lesson["progress_percent"] == 90
    assert lesson["resume_position_seconds"] == 90


def test_next_required_video_is_locked_until_the_previous_one_is_completed(client, db_session, sample_lesson) -> None:
    from app.models.catalog import Lesson
    from app.models.enums import LessonType

    second_lesson = Lesson(module_id=sample_lesson.lesson.module_id, title="Segunda lección", lesson_type=LessonType.VIDEO, position=2, duration_seconds=100)
    db_session.add(second_lesson)
    db_session.commit()

    test_client, _ = client
    before_completion = test_client.get(f"/api/cursos/{sample_lesson.course.slug}")
    assert before_completion.status_code == 200
    assert before_completion.json()["modules"][0]["lessons"][1]["unlocked"] is False
    assert test_client.get(f"/api/lessons/{second_lesson.id}").status_code == 403

    first_completed = test_client.post(f"/api/lessons/{sample_lesson.lesson.id}/progress", json={"position_seconds": 90, "duration_seconds": 100, "ranges": [{"start": 0, "end": 90}]})
    assert first_completed.status_code == 200

    after_completion = test_client.get(f"/api/cursos/{sample_lesson.course.slug}")
    assert after_completion.json()["modules"][0]["lessons"][1]["unlocked"] is True
    assert test_client.get(f"/api/lessons/{second_lesson.id}").status_code == 200


def test_dashboard_awards_experience_and_one_badge_per_completed_course(client, sample_lesson) -> None:
    test_client, _ = client
    completed = test_client.post(
        f"/api/lessons/{sample_lesson.lesson.id}/progress",
        json={"position_seconds": 90, "duration_seconds": 100, "ranges": [{"start": 0, "end": 90}]},
    )
    assert completed.status_code == 200

    dashboard = test_client.get("/api/dashboard")

    assert dashboard.status_code == 200
    assert dashboard.json()["experience"] == {"points": 100, "level": 1, "points_to_next_level": 400}
    assert dashboard.json()["badges"] == [{"title": "Curso de pruebas", "course_slug": "curso-pruebas", "awarded_at": dashboard.json()["badges"][0]["awarded_at"]}]
