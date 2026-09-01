import re
import unicodedata
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import Academy, Course, LearningPathCourse, Lesson, Module
from app.models.enums import LessonType
from app.models.identity import Group, User
from app.providers.auth.base import AuthenticatedUser
from app.services.graph import GraphService

SUPPORTED_DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.ms-excel",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
}
SUPPORTED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]", "", value)


def _lesson_type(item: dict) -> Optional[LessonType]:
    if item["is_video"]:
        return LessonType.VIDEO
    extension = "." + item["name"].rsplit(".", 1)[-1].lower() if "." in item["name"] else ""
    if item.get("mime_type") in SUPPORTED_DOCUMENT_MIME_TYPES or extension in SUPPORTED_DOCUMENT_EXTENSIONS:
        return LessonType.DOCUMENT
    return None


def _walk_drive(graph: GraphService, drive_id: str, parent_id: str, token: str, units: Dict[str, str], current_unit: str = "", depth: int = 0) -> Dict[str, List[dict]]:
    if depth > 4:
        return {}
    results: Dict[str, List[dict]] = {}
    for item in graph.list_children(drive_id, parent_id, token):
        item_unit = units.get(normalize(item["name"]), current_unit) if item["is_folder"] else current_unit
        lesson_type = _lesson_type(item)
        if lesson_type and item_unit:
            results.setdefault(item_unit, []).append({**item, "drive_id": drive_id, "lesson_type": lesson_type})
        elif item["is_folder"]:
            for unit, videos in _walk_drive(graph, drive_id, item["id"], token, units, item_unit, depth + 1).items():
                results.setdefault(unit, []).extend(videos)
    return results


def sync_user_catalog(session: Session, user: AuthenticatedUser) -> dict:
    """Mirror visible SharePoint folders into the existing Academy catalog for one user."""
    academies = session.scalars(select(Academy).options(selectinload(Academy.learning_paths)).where(Academy.is_published.is_(True))).all()
    units = {normalize(academy.name): academy.slug for academy in academies}
    graph = GraphService()
    site = graph.inspect_site(user.access_token or "")
    resources_by_unit: Dict[str, List[dict]] = {}
    visible_units = set()
    for drive in site["drives"]:
        for root_item in drive["items"]:
            root_unit = units.get(normalize(root_item["name"]), "") if root_item["is_folder"] else ""
            if root_unit:
                visible_units.add(root_unit)
            if root_item["is_folder"]:
                for unit, resources in _walk_drive(graph, drive["id"], root_item["id"], user.access_token or "", units, root_unit).items():
                    visible_units.add(unit)
                    resources_by_unit.setdefault(unit, []).extend(resources)

    database_user = session.scalar(select(User).options(selectinload(User.groups)).where(User.id == user.id))
    groups = session.scalars(select(Group).where(Group.name.in_([f"ACADEMIA-{slug.removeprefix('unidad-').upper()}" for slug in visible_units]))).all()
    if database_user:
        database_user.groups = groups

    for academy in academies:
        academy_resources = resources_by_unit.get(academy.slug, [])
        if not academy_resources:
            continue
        path = next((item for item in academy.learning_paths if item.is_published), None)
        if path is None:
            continue
        link = session.scalar(select(LearningPathCourse).where(LearningPathCourse.learning_path_id == path.id).order_by(LearningPathCourse.position))
        if link is None:
            continue
        course = session.get(Course, link.course_id, options=[selectinload(Course.modules).selectinload(Module.lessons)])
        if course is None:
            continue
        module = next(iter(course.modules), None)
        if module is None:
            module = Module(course_id=course.id, title="Videos", position=1)
            session.add(module)
            session.flush()
        placeholders = [lesson for lesson in module.lessons if (lesson.sharepoint_item_id or "").startswith("demo-item-")]
        for position, resource in enumerate(academy_resources, start=1):
            lesson = session.scalar(select(Lesson).where(Lesson.sharepoint_drive_id == resource["drive_id"], Lesson.sharepoint_item_id == resource["id"]))
            if lesson is None:
                lesson = placeholders.pop(0) if placeholders else Lesson(module_id=module.id, title=resource["name"], lesson_type=resource["lesson_type"], position=position)
                session.add(lesson)
            lesson.title = resource["name"]
            lesson.lesson_type = resource["lesson_type"]
            lesson.position = position
            lesson.is_required = resource["lesson_type"] == LessonType.VIDEO
            lesson.duration_seconds = resource.get("duration_seconds") if resource["lesson_type"] == LessonType.VIDEO else None
            lesson.sharepoint_site_id = site["site"]["id"]
            lesson.sharepoint_drive_id = resource["drive_id"]
            lesson.sharepoint_item_id = resource["id"]
            lesson.document_url = resource.get("web_url") if resource["lesson_type"] == LessonType.DOCUMENT else None
    session.commit()
    resources = [resource for items in resources_by_unit.values() for resource in items]
    return {
        "visible_academies": len(visible_units),
        "videos_imported": sum(resource["lesson_type"] == LessonType.VIDEO for resource in resources),
        "documents_imported": sum(resource["lesson_type"] == LessonType.DOCUMENT for resource in resources),
    }
