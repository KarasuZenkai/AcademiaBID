from app.models.catalog import Academy, Course, LearningPath, Lesson, Module
from app.models.identity import User
from app.models.enums import Role
from app.models.progress import LearningPathAssignment
from app.providers.auth.base import AuthenticatedUser
from app.services.access import academy_allowed, path_allowed
from app.services.sharepoint_sync import sync_user_catalog


class FakeGraph:
    def inspect_site(self, _token):
        return {"site": {"id": "site-1"}, "drives": [{"id": "drive-1", "items": [{"id": "academy-1", "name": "01_Nuevo_ingreso", "is_folder": True}]}]}

    def list_children(self, _drive_id, item_id, _token):
        children = {
            "academy-1": [{"id": "path-1", "name": "01_Induccion_general", "is_folder": True}],
            "path-1": [{"id": "course-1", "name": "01_Bienvenida_a_BID", "is_folder": True}],
            "course-1": [{"id": "module-1", "name": "01_Cultura_y_valores", "is_folder": True}],
            "module-1": [
                {"id": "video-1", "name": "01_Bienvenida.mp4", "is_folder": False, "is_video": True, "mime_type": "video/mp4", "duration_seconds": 60, "web_url": "https://example.test/video"},
                {"id": "document-1", "name": "02_Codigo_de_conducta.pdf", "is_folder": False, "is_video": False, "mime_type": "application/pdf", "duration_seconds": None, "web_url": "https://example.test/document"},
            ],
        }
        return children[item_id]


def test_sync_creates_sharepoint_hierarchy_and_locks_new_academy(db_session, sample_lesson, monkeypatch):
    monkeypatch.setattr("app.services.sharepoint_sync.GraphService", FakeGraph)

    result = sync_user_catalog(db_session, sample_lesson.user)

    academy = db_session.query(Academy).filter_by(name="Nuevo ingreso").one()
    path = db_session.query(LearningPath).filter_by(name="Induccion general").one()
    course = db_session.query(Course).filter_by(title="Bienvenida a BID").one()
    module = db_session.query(Module).filter_by(title="Cultura y valores").one()
    assert path.academy_id == academy.id
    assert module.course_id == course.id
    assert db_session.query(Lesson).filter_by(module_id=module.id).count() == 2
    assert result["videos_imported"] == 1
    assert result["documents_imported"] == 1
    assert not academy_allowed(db_session, academy, sample_lesson.user)

    sync_user_catalog(db_session, sample_lesson.user)
    assert db_session.query(Academy).filter_by(name="Nuevo ingreso").count() == 1
    assert db_session.query(Lesson).filter_by(module_id=module.id).count() == 2

    learner = User(external_id="path-user", name="Path User", email="path@example.test", role=Role.LEARNER)
    db_session.add(learner); db_session.flush()
    db_session.add(LearningPathAssignment(user_id=learner.id, learning_path_id=path.id)); db_session.commit()
    learner_auth = AuthenticatedUser(id=learner.id, external_id=learner.external_id, name=learner.name, email=learner.email, role=Role.LEARNER, groups=())
    assert path_allowed(db_session, path, learner_auth)
