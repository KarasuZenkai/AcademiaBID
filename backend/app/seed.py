"""Idempotent local data for validating the initial relational schema."""
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.enums import LessonType, Role
from app.models.identity import Group, User

DEMO_UNITS = [
    ("Energy", "comercial"),
    ("Deportes", "general"),
    ("Tecnología", "tecnologia"),
    ("Agua", "general"),
    ("Jurídico", "gerentes"),
    ("Contabilidad", "gerentes"),
    ("Finanzas", "comercial"),
    ("Construcción", "gerentes"),
    ("Talento Humano", "general"),
    ("TI", "tecnologia"),
    ("Prosper", "comercial"),
]

DEMO_SITE_ID = "demo-centro-aprendizaje"
DEMO_DRIVE_ID = "demo-biblioteca-academia-bid"


def one_or_create(session, model, defaults=None, **lookup):
    instance = session.scalar(select(model).filter_by(**lookup))
    if instance is None:
        instance = model(**lookup, **(defaults or {}))
        session.add(instance)
        session.flush()
    return instance


def seed() -> None:
    with SessionLocal.begin() as session:
        general = one_or_create(session, Group, name="GENERAL", defaults={"description": "Acceso corporativo general"})
        technology = one_or_create(session, Group, name="TECNOLOGIA", defaults={"description": "Equipo de tecnología"})
        commercial = one_or_create(session, Group, name="COMERCIAL", defaults={"description": "Equipo comercial"})
        managers = one_or_create(session, Group, name="GERENTES", defaults={"description": "Liderazgo"})

        admin = one_or_create(session, User, email="admin@local.test", defaults={"name": "Administrador", "external_id": "dev-admin-001", "role": Role.ADMIN})
        tech_user = one_or_create(session, User, email="tecnologia@local.test", defaults={"name": "Usuario Tecnología", "external_id": "dev-tech-001"})
        commercial_user = one_or_create(session, User, email="comercial@local.test", defaults={"name": "Usuario Comercial", "external_id": "dev-commercial-001"})
        general_user = one_or_create(session, User, email="usuario@local.test", defaults={"name": "Usuario General", "external_id": "dev-user-001"})
        manager_user = one_or_create(session, User, email="gerentes@local.test", defaults={"name": "Usuario Gerentes", "external_id": "dev-manager-001"})

        for legacy_slug in ("academia-general", "academia-tecnologia", "academia-comercial"):
            legacy_academy = session.scalar(select(Academy).where(Academy.slug == legacy_slug))
            if legacy_academy:
                legacy_academy.is_published = False

        unit_groups = {}
        for position, (unit_name, _audience) in enumerate(DEMO_UNITS, start=1):
            slug = unit_name.lower().replace("í", "i").replace("ó", "o").replace(" ", "-")
            unit_group = one_or_create(
                session,
                Group,
                name=f"ACADEMIA-{slug.upper()}",
                defaults={"description": f"Acceso demo a Academia BID / {unit_name}"},
            )
            unit_groups[unit_name] = unit_group
            academy = one_or_create(session, Academy, slug=f"unidad-{slug}", defaults={"name": unit_name, "description": f"Academia demo de la unidad de negocio {unit_name}.", "is_published": True})
            path = one_or_create(session, LearningPath, slug=f"ruta-{slug}", defaults={"academy": academy, "name": f"Inducción a {unit_name}", "description": "Ruta demo de incorporación.", "position": position, "is_published": True})
            course = one_or_create(session, Course, slug=f"fundamentos-{slug}", defaults={"title": f"Fundamentos de {unit_name}", "description": "Curso demo para validar el catálogo.", "estimated_minutes": 20, "is_published": True})
            academy.groups = [unit_group]
            course.groups = [unit_group]
            if session.get(LearningPathCourse, {"learning_path_id": path.id, "course_id": course.id}) is None:
                session.add(LearningPathCourse(learning_path=path, course=course, position=1, is_required=True))
            module = one_or_create(session, Module, course_id=course.id, position=1, defaults={"title": "Introducción", "description": "Módulo demo"})
            lesson = one_or_create(session, Lesson, module_id=module.id, position=1, defaults={"title": f"Bienvenida a {unit_name}", "lesson_type": LessonType.VIDEO, "duration_seconds": 5})
            lesson.lesson_type = LessonType.VIDEO
            lesson.document_url = None
            lesson.duration_seconds = 5
            lesson.sharepoint_site_id = DEMO_SITE_ID
            lesson.sharepoint_drive_id = DEMO_DRIVE_ID
            lesson.sharepoint_item_id = f"demo-item-{slug}-bienvenida"

        admin.groups = [general, technology, commercial, managers, *unit_groups.values()]
        tech_user.groups = [general, technology, unit_groups["Tecnología"], unit_groups["TI"]]
        commercial_user.groups = [general, commercial, unit_groups["Energy"], unit_groups["Finanzas"], unit_groups["Prosper"]]
        general_user.groups = [general, unit_groups["Deportes"], unit_groups["Agua"], unit_groups["Talento Humano"]]
        manager_user.groups = [general, managers, unit_groups["Jurídico"], unit_groups["Contabilidad"], unit_groups["Construcción"]]


if __name__ == "__main__":
    seed()
    print("Seed data applied.")
