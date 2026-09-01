from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Iterator
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registers every model with Base.metadata
from app.api.dependencies import get_current_user, get_db_session
from app.db.base import Base
from app.main import app
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.identity import User
from app.models.progress import Enrollment
from app.models.enums import LessonType, Role
from app.providers.auth.base import AuthenticatedUser


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False)


@dataclass
class SampleLesson:
    lesson: Lesson
    course: Course
    user: AuthenticatedUser


@pytest.fixture
def db_session() -> Iterator[Session]:
    Base.metadata.create_all(TEST_ENGINE)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(TEST_ENGINE)


@pytest.fixture
def sample_lesson(db_session: Session) -> SampleLesson:
    database_user = User(
        external_id="test-learner",
        name="Test Learner",
        email="learner@example.test",
        role=Role.LEARNER,
    )
    academy = Academy(name="Academia de pruebas", slug="pruebas", is_published=True)
    learning_path = LearningPath(
        academy=academy,
        name="Ruta de pruebas",
        slug="ruta-pruebas",
        is_published=True,
    )
    course = Course(
        title="Curso de pruebas",
        slug="curso-pruebas",
        is_published=True,
    )
    module = Module(course=course, title="Módulo de pruebas", position=1)
    lesson = Lesson(
        module=module,
        title="Lección de pruebas",
        lesson_type=LessonType.VIDEO,
        position=1,
        duration_seconds=100,
        completion_threshold=Decimal("0.90"),
    )
    db_session.add_all([database_user, academy, learning_path, course, module, lesson])
    db_session.flush()
    db_session.add(LearningPathCourse(learning_path_id=learning_path.id, course_id=course.id, position=1))
    db_session.add(Enrollment(user_id=database_user.id, course_id=course.id))
    db_session.commit()

    return SampleLesson(
        lesson=lesson,
        course=course,
        user=AuthenticatedUser(
            id=database_user.id,
            external_id=database_user.external_id,
            name=database_user.name,
            email=database_user.email,
            role=Role.LEARNER,
            groups=(),
        ),
    )


@pytest.fixture
def client(
    db_session: Session, sample_lesson: SampleLesson
) -> Iterator[tuple[TestClient, Callable[[AuthenticatedUser], None]]]:
    def override_db_session() -> Iterator[Session]:
        yield db_session

    def set_current_user(user: AuthenticatedUser) -> None:
        app.dependency_overrides[get_current_user] = lambda: user

    app.dependency_overrides[get_db_session] = override_db_session
    set_current_user(sample_lesson.user)
    with TestClient(app) as test_client:
        yield test_client, set_current_user
    app.dependency_overrides.clear()


def make_authenticated_user(role: Role, groups: tuple[str, ...] = ()) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=uuid.uuid4(),
        external_id=f"test-{role.value}",
        name=f"Test {role.value}",
        email=f"{role.value}@example.test",
        role=role,
        groups=groups,
    )
