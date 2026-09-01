import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db_session
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.enums import Role
from app.providers.auth.base import AuthenticatedUser
from app.schemas.admin import AcademyWrite, CourseWrite, LessonWrite, ModuleWrite, PathCourseWrite, PathWrite
from app.services.audit import log_admin_action

router = APIRouter(prefix="/api/admin", tags=["admin"])
admin_only = Depends(require_roles(Role.ADMIN))

def entity(session, model, item_id):
    item = session.get(model, item_id)
    if item is None: raise HTTPException(status_code=404, detail="Resource not found")
    return item

def save(session, item, actor, action, kind):
    session.add(item); session.flush(); log_admin_action(session, actor.id, action, kind, item.id); session.commit(); session.refresh(item); return item

@router.get("/overview")
def overview(session: Session = Depends(get_db_session), _: AuthenticatedUser = admin_only):
    return {"academies": [{"id": str(a.id), "name": a.name, "slug": a.slug, "published": a.is_published} for a in session.scalars(select(Academy).order_by(Academy.name))], "paths": [{"id": str(p.id), "name": p.name, "academy_id": str(p.academy_id)} for p in session.scalars(select(LearningPath).order_by(LearningPath.name))], "courses": [{"id": str(c.id), "title": c.title, "slug": c.slug, "published": c.is_published} for c in session.scalars(select(Course).order_by(Course.title))], "modules": [{"id": str(m.id), "title": m.title, "course_id": str(m.course_id)} for m in session.scalars(select(Module).order_by(Module.title))]}

@router.post("/academies", status_code=201)
def create_academy(payload: AcademyWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    return {"id": str(save(session, Academy(**payload.model_dump()), actor, "CREATE_ACADEMY", "academy").id)}

@router.patch("/academies/{academy_id}")
def update_academy(academy_id: uuid.UUID, payload: AcademyWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    item=entity(session, Academy, academy_id); before=item.is_published
    for key, value in payload.model_dump().items(): setattr(item,key,value)
    action="PUBLISH_ACADEMY" if not before and item.is_published else "UNPUBLISH_ACADEMY" if before and not item.is_published else "UPDATE_ACADEMY"
    return {"id": str(save(session,item,actor,action,"academy").id)}

@router.post("/learning-paths", status_code=201)
def create_path(payload: PathWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    entity(session, Academy, payload.academy_id); return {"id": str(save(session, LearningPath(**payload.model_dump()), actor,"CREATE_LEARNING_PATH","learning_path").id)}

@router.patch("/learning-paths/{path_id}")
def update_path(path_id: uuid.UUID, payload: PathWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    item=entity(session,LearningPath,path_id)
    for key,value in payload.model_dump().items(): setattr(item,key,value)
    return {"id":str(save(session,item,actor,"UPDATE_LEARNING_PATH","learning_path").id)}

@router.post("/learning-paths/{path_id}/courses", status_code=201)
def add_course_to_path(path_id: uuid.UUID, payload: PathCourseWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    entity(session, LearningPath, path_id); entity(session, Course, payload.course_id)
    if session.get(LearningPathCourse, {"learning_path_id": path_id, "course_id": payload.course_id}): raise HTTPException(status_code=409, detail="Course is already in this learning path")
    link=LearningPathCourse(learning_path_id=path_id, **payload.model_dump()); session.add(link); session.flush(); log_admin_action(session, actor.id, "ADD_COURSE_TO_PATH", "learning_path", path_id, {"course_id": str(payload.course_id)}); session.commit(); return {"learning_path_id": str(path_id), "course_id": str(payload.course_id)}

@router.post("/courses", status_code=201)
def create_course(payload: CourseWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    return {"id":str(save(session,Course(**payload.model_dump()),actor,"CREATE_COURSE","course").id)}

@router.patch("/courses/{course_id}")
def update_course(course_id: uuid.UUID, payload: CourseWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    item=entity(session,Course,course_id); before=item.is_published
    for key,value in payload.model_dump().items(): setattr(item,key,value)
    action="PUBLISH_COURSE" if not before and item.is_published else "UNPUBLISH_COURSE" if before and not item.is_published else "UPDATE_COURSE"
    return {"id":str(save(session,item,actor,action,"course").id)}

@router.post("/courses/{course_id}/modules", status_code=201)
def create_module(course_id: uuid.UUID, payload: ModuleWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    if payload.course_id != course_id: raise HTTPException(status_code=422,detail="course_id must match URL")
    entity(session,Course,course_id); return {"id":str(save(session,Module(**payload.model_dump()),actor,"CREATE_MODULE","module").id)}

@router.patch("/modules/{module_id}")
def update_module(module_id: uuid.UUID, payload: ModuleWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    item=entity(session,Module,module_id)
    for key,value in payload.model_dump().items(): setattr(item,key,value)
    return {"id":str(save(session,item,actor,"UPDATE_MODULE","module").id)}

@router.post("/modules/{module_id}/lessons", status_code=201)
def create_lesson(module_id: uuid.UUID, payload: LessonWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    if payload.module_id != module_id: raise HTTPException(status_code=422,detail="module_id must match URL")
    entity(session,Module,module_id); return {"id":str(save(session,Lesson(**payload.model_dump()),actor,"CREATE_LESSON","lesson").id)}

@router.patch("/lessons/{lesson_id}")
def update_lesson(lesson_id: uuid.UUID, payload: LessonWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    item=entity(session,Lesson,lesson_id)
    for key,value in payload.model_dump().items(): setattr(item,key,value)
    return {"id":str(save(session,item,actor,"UPDATE_LESSON","lesson").id)}
