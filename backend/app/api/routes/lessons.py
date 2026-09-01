import uuid
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.catalog import Course, Lesson, Module
from app.models.progress import LessonProgress, VideoSession
from app.models.common import utcnow
from app.models.enums import LessonType, ProgressStatus
from app.providers.auth.base import AuthenticatedUser
from app.providers.media.factory import get_media_provider
from app.core.config import get_settings
from app.services.graph import GraphService
from app.schemas.progress import ProgressRead, ProgressWrite
from app.services.tracking import apply_video_progress, update_course_completion
from app.services.sequencing import next_lesson, unlocked_lesson_ids
from app.services.access import course_unlocked, module_allowed

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

def get_authorized_lesson(lesson_id: uuid.UUID, session: Session, user: AuthenticatedUser) -> Lesson:
    lesson = session.get(Lesson, lesson_id, options=[joinedload(Lesson.module).joinedload(Module.course).joinedload(Course.groups), joinedload(Lesson.module).joinedload(Module.course).selectinload(Course.modules).selectinload(Module.lessons)])
    allowed = lesson and module_allowed(session, lesson.module, user)
    if not allowed: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    if not course_unlocked(session, lesson.module.course, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Complete the required course before accessing this course")
    progress_records = session.scalars(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id.in_([item.id for module in lesson.module.course.modules for item in module.lessons]))).all()
    if lesson.id not in unlocked_lesson_ids(lesson.module.course, progress_records):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Complete the previous required lesson to unlock this lesson")
    return lesson

@router.get("/{lesson_id}")
def lesson_detail(lesson_id: uuid.UUID, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)):
    lesson = get_authorized_lesson(lesson_id, session, user)
    following = next_lesson(lesson.module.course, lesson.id)
    return {"id": str(lesson.id), "title": lesson.title, "description": lesson.description, "lesson_type": lesson.lesson_type.value, "duration_seconds": lesson.duration_seconds, "external_url": lesson.external_url, "next_lesson": {"id": str(following.id), "title": following.title} if following else None}

@router.post("/{lesson_id}/playback")
def playback(lesson_id: uuid.UUID, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)):
    lesson = get_authorized_lesson(lesson_id, session, user)
    if lesson.lesson_type != LessonType.VIDEO: raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Playback is only available for VIDEO lessons")
    if get_settings().auth_provider == "entra" and user.access_token:
        if not lesson.sharepoint_drive_id or not lesson.sharepoint_item_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This lesson has not been synchronized from SharePoint")
        source_url = GraphService().playback_url(lesson.sharepoint_drive_id, lesson.sharepoint_item_id, user.access_token)
    else:
        try:
            source_url = get_media_provider().get_playback_source(lesson.sharepoint_site_id, lesson.sharepoint_drive_id, lesson.sharepoint_item_id).url
        except NotImplementedError as error:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(error)) from error
    progress = session.scalar(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id))
    video_session = VideoSession(user_id=user.id, lesson_id=lesson.id)
    session.add(video_session); session.commit(); session.refresh(video_session)
    return {"url": source_url, "expires_at": None, "duration_seconds": lesson.duration_seconds, "resume_position": progress.last_position_seconds if progress else 0, "session_id": str(video_session.id)}


@router.get("/{lesson_id}/download")
def download_document(lesson_id: uuid.UUID, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> Response:
    lesson = get_authorized_lesson(lesson_id, session, user)
    if lesson.lesson_type != LessonType.DOCUMENT:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Download is only available for DOCUMENT lessons")
    if get_settings().auth_provider != "entra" or not user.access_token or not lesson.sharepoint_drive_id or not lesson.sharepoint_item_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This document is not available for download")
    content, media_type = GraphService().download_file(lesson.sharepoint_drive_id, lesson.sharepoint_item_id, user.access_token)
    filename = quote(lesson.title, safe="")
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}", "Cache-Control": "private, no-store"})


@router.get("/{lesson_id}/thumbnail", responses={204: {"description": "No thumbnail is available"}})
def thumbnail(lesson_id: uuid.UUID, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)) -> Response:
    lesson = session.get(Lesson, lesson_id, options=[joinedload(Lesson.module).joinedload(Module.course).joinedload(Course.groups)])
    allowed = lesson and module_allowed(session, lesson.module, user) and course_unlocked(session, lesson.module.course, user)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    if lesson.lesson_type != LessonType.VIDEO or get_settings().auth_provider != "entra" or not user.access_token or not lesson.sharepoint_drive_id or not lesson.sharepoint_item_id:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    image = GraphService().thumbnail(lesson.sharepoint_drive_id, lesson.sharepoint_item_id, user.access_token)
    if image is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    content, media_type = image
    return Response(content=content, media_type=media_type, headers={"Cache-Control": "private, max-age=300"})

@router.post("/{lesson_id}/progress", response_model=ProgressRead)
def progress(lesson_id: uuid.UUID, payload: ProgressWrite, session: Session = Depends(get_db_session), user: AuthenticatedUser = Depends(get_current_user)):
    lesson = get_authorized_lesson(lesson_id, session, user)
    if lesson.lesson_type != LessonType.VIDEO: raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Progress tracking is only available for VIDEO lessons")
    video_session = None
    if payload.session_id:
        video_session = session.get(VideoSession, payload.session_id)
        if video_session is None or video_session.user_id != user.id or video_session.lesson_id != lesson.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid video session")
        video_session.last_activity_at = utcnow()
    try:
        progress_record, percentage = apply_video_progress(session, user.id, lesson, payload.position_seconds, payload.duration_seconds, [(int(item.start), int(item.end)) for item in payload.ranges], payload.session_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    course_percentage = update_course_completion(session, user.id, lesson.module.course_id)
    if video_session and progress_record.status == ProgressStatus.COMPLETED:
        video_session.ended_at = utcnow()
    session.commit()
    return ProgressRead(watched_seconds=progress_record.watched_seconds, progress_percent=round(percentage, 2), last_position_seconds=progress_record.last_position_seconds, completed=progress_record.status == ProgressStatus.COMPLETED, course_progress_percent=round(course_percentage, 2))
