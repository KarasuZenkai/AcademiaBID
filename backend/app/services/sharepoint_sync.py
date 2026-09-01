"""Synchronize the governed SharePoint folder hierarchy into Academia BID."""

import re
import unicodedata
from typing import List, Optional, Tuple, Type

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.enums import LessonType
from app.models.identity import Group
from app.providers.auth.base import AuthenticatedUser
from app.services.graph import GraphService

SUPPORTED_DOCUMENT_MIME_TYPES = {
    "application/pdf", "application/msword", "application/vnd.ms-excel", "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation", "text/plain",
}
SUPPORTED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}
ORDER_PREFIX = re.compile(r"^\s*(\d+)\s*[_\-. ]+\s*(.+?)\s*$")


def display_name(value: str) -> str:
    """Remove an optional ordering prefix, retaining the original human name."""
    match = ORDER_PREFIX.match(value)
    return match.group(2).replace("_", " ").strip() if match else value.replace("_", " ").strip()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", display_name(value)).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]", "", value)


def sort_key(item: dict) -> Tuple[int, str]:
    match = ORDER_PREFIX.match(item["name"])
    return (int(match.group(1)) if match else 999999, item["name"].lower())


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", ascii_value)) or "contenido"


def _lesson_type(item: dict) -> Optional[LessonType]:
    if item["is_video"]:
        return LessonType.VIDEO
    extension = "." + item["name"].rsplit(".", 1)[-1].lower() if "." in item["name"] else ""
    if item.get("mime_type") in SUPPORTED_DOCUMENT_MIME_TYPES or extension in SUPPORTED_DOCUMENT_EXTENSIONS:
        return LessonType.DOCUMENT
    return None


def _children(graph: GraphService, drive_id: str, parent_id: str, token: str) -> List[dict]:
    return sorted(graph.list_children(drive_id, parent_id, token), key=sort_key)


def _by_folder_identity(session: Session, model: Type, drive_id: str, item_id: str):
    return session.scalar(select(model).where(model.sharepoint_drive_id == drive_id, model.sharepoint_item_id == item_id))


def _unique_slug(session: Session, model: Type, preferred: str) -> str:
    candidate, counter = preferred, 2
    while session.scalar(select(model.id).where(model.slug == candidate)) is not None:
        candidate = f"{preferred}-{counter}"
        counter += 1
    return candidate


def _academy(session: Session, drive_id: str, folder: dict) -> Academy:
    item = _by_folder_identity(session, Academy, drive_id, folder["id"])
    name = display_name(folder["name"])
    if item is None:
        item = next((academy for academy in session.scalars(select(Academy)).all() if normalize(academy.name) == normalize(name)), None)
    if item is None:
        slug = _unique_slug(session, Academy, slugify(name))
        item = Academy(name=name, slug=slug, description=f"Contenido sincronizado desde SharePoint: {name}.", is_published=True)
        lock_group = Group(name=f"ACADEMIA-CONTENT-{slug.upper()[:90]}", description="Contenido pendiente de asignación en Academia BID")
        item.groups = [lock_group]
        session.add(item)
    item.name = name; item.sharepoint_drive_id = drive_id; item.sharepoint_item_id = folder["id"]
    session.flush()
    return item


def _path(session: Session, academy: Academy, drive_id: str, folder: dict, position: int) -> LearningPath:
    item = _by_folder_identity(session, LearningPath, drive_id, folder["id"])
    name = display_name(folder["name"])
    if item is None:
        item = next((path for path in academy.learning_paths if normalize(path.name) == normalize(name)), None)
    if item is None:
        item = LearningPath(academy=academy, name=name, slug=_unique_slug(session, LearningPath, f"{academy.slug}-{slugify(name)}"), description=f"Ruta sincronizada: {name}.", position=position, is_published=True)
        session.add(item)
    item.name = name; item.is_published = True; item.sharepoint_drive_id = drive_id; item.sharepoint_item_id = folder["id"]
    session.flush()
    return item


def _course(session: Session, academy: Academy, path: LearningPath, drive_id: str, folder: dict, position: int) -> Course:
    item = _by_folder_identity(session, Course, drive_id, folder["id"])
    name = display_name(folder["name"])
    if item is None:
        existing = session.scalars(select(Course).join(LearningPathCourse).where(LearningPathCourse.learning_path_id == path.id)).all()
        item = next((course for course in existing if normalize(course.title) == normalize(name)), None)
    if item is None:
        item = Course(title=name, slug=_unique_slug(session, Course, f"{academy.slug}-{path.slug}-{slugify(name)}"), description=f"Curso sincronizado: {name}.", is_published=True)
        session.add(item); session.flush()
    item.title = name; item.is_published = True; item.sharepoint_drive_id = drive_id; item.sharepoint_item_id = folder["id"]
    if session.get(LearningPathCourse, {"learning_path_id": path.id, "course_id": item.id}) is None:
        next_position = (max((link.position for link in path.course_links), default=0) + 1)
        session.add(LearningPathCourse(learning_path=path, course=item, position=next_position, is_required=True))
    session.flush()
    return item


def _module(session: Session, course: Course, drive_id: str, folder: dict, position: int) -> Module:
    item = _by_folder_identity(session, Module, drive_id, folder["id"])
    name = display_name(folder["name"])
    if item is None:
        item = next((module for module in course.modules if normalize(module.title) == normalize(name)), None)
    if item is None:
        item = Module(course=course, title=name, position=max((module.position for module in course.modules), default=0) + 1)
        session.add(item)
    item.title = name; item.sharepoint_drive_id = drive_id; item.sharepoint_item_id = folder["id"]
    session.flush()
    return item


def _lesson(session: Session, module: Module, site_id: str, drive_id: str, resource: dict, position: int) -> bool:
    lesson_type = _lesson_type(resource)
    if lesson_type is None:
        return False
    lesson = session.scalar(select(Lesson).where(Lesson.sharepoint_drive_id == drive_id, Lesson.sharepoint_item_id == resource["id"]))
    if lesson is None:
        lesson = Lesson(module=module, title=display_name(resource["name"]), lesson_type=lesson_type, position=max((item.position for item in module.lessons), default=0) + 1)
        session.add(lesson)
    lesson.module = module; lesson.title = display_name(resource["name"]); lesson.lesson_type = lesson_type
    lesson.is_required = lesson_type == LessonType.VIDEO; lesson.duration_seconds = resource.get("duration_seconds") if lesson_type == LessonType.VIDEO else None
    lesson.sharepoint_site_id = site_id; lesson.sharepoint_drive_id = drive_id; lesson.sharepoint_item_id = resource["id"]
    lesson.document_url = resource.get("web_url") if lesson_type == LessonType.DOCUMENT else None
    return True


def sync_user_catalog(session: Session, user: AuthenticatedUser) -> dict:
    """Mirror Academy > Path > Course > Module > files from SharePoint folders.

    New academies are deliberately locked by an empty internal group until an
    administrator creates a direct assignment in Academia BID.
    """
    graph = GraphService(); site = graph.inspect_site(user.access_token or "")
    counts = {"academies": 0, "paths": 0, "courses": 0, "modules": 0, "videos": 0, "documents": 0, "ignored_files": 0}
    for drive in site["drives"]:
        for academy_folder in (item for item in drive["items"] if item["is_folder"]):
            path_folders = [item for item in _children(graph, drive["id"], academy_folder["id"], user.access_token or "") if item["is_folder"]]
            if not path_folders:
                continue
            academy = _academy(session, drive["id"], academy_folder); counts["academies"] += 1
            for path_position, path_folder in enumerate(path_folders, start=1):
                course_folders = [item for item in _children(graph, drive["id"], path_folder["id"], user.access_token or "") if item["is_folder"]]
                if not course_folders:
                    continue
                path = _path(session, academy, drive["id"], path_folder, path_position); counts["paths"] += 1
                for course_position, course_folder in enumerate(course_folders, start=1):
                    module_folders = [item for item in _children(graph, drive["id"], course_folder["id"], user.access_token or "") if item["is_folder"]]
                    if not module_folders:
                        continue
                    course = _course(session, academy, path, drive["id"], course_folder, course_position); counts["courses"] += 1
                    for module_position, module_folder in enumerate(module_folders, start=1):
                        module = _module(session, course, drive["id"], module_folder, module_position); counts["modules"] += 1
                        for lesson_position, resource in enumerate(_children(graph, drive["id"], module_folder["id"], user.access_token or ""), start=1):
                            if resource["is_folder"]:
                                continue
                            if _lesson(session, module, site["site"]["id"], drive["id"], resource, lesson_position):
                                counts["videos" if resource["is_video"] else "documents"] += 1
                            else:
                                counts["ignored_files"] += 1
    session.commit()
    return {"visible_academies": counts["academies"], "videos_imported": counts["videos"], "documents_imported": counts["documents"], "paths_synced": counts["paths"], "courses_synced": counts["courses"], "modules_synced": counts["modules"], "ignored_files": counts["ignored_files"]}
