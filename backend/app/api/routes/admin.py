import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased
from app.api.dependencies import get_current_user
from app.core.permissions import require_roles
from app.db.session import get_db_session
from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.identity import User
from app.models.progress import AcademyAssignment, CoursePrerequisite, Enrollment, LearningPathAssignment, ModuleAssignment
from app.models.enums import Role
from app.providers.auth.base import AuthenticatedUser
from app.schemas.admin import AcademyWrite, AssignmentTarget, AssignmentWrite, CourseWrite, LessonWrite, ModuleWrite, PathCourseWrite, PathWrite, PrerequisiteWrite
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
    return {
        "users": [{"id": str(user.id), "name": user.name, "email": user.email, "role": user.role.value, "active": user.is_active} for user in session.scalars(select(User).order_by(User.name))],
        "academies": [{"id": str(a.id), "name": a.name, "slug": a.slug, "published": a.is_published} for a in session.scalars(select(Academy).order_by(Academy.name))],
        "paths": [{"id": str(p.id), "name": p.name, "academy_id": str(p.academy_id)} for p in session.scalars(select(LearningPath).order_by(LearningPath.name))],
        "courses": [{"id": str(c.id), "title": c.title, "slug": c.slug, "published": c.is_published} for c in session.scalars(select(Course).order_by(Course.title))],
        "modules": [{"id": str(m.id), "title": m.title, "course_id": str(m.course_id)} for m in session.scalars(select(Module).order_by(Module.title))],
    }


ASSIGNMENT_MODELS = {
    AssignmentTarget.ACADEMY: (AcademyAssignment, "academy_id", Academy, "academia"),
    AssignmentTarget.LEARNING_PATH: (LearningPathAssignment, "learning_path_id", LearningPath, "ruta"),
    AssignmentTarget.COURSE: (Enrollment, "course_id", Course, "curso"),
    AssignmentTarget.MODULE: (ModuleAssignment, "module_id", Module, "módulo"),
}


def assignment_records(session: Session) -> list[dict]:
    records = []
    for target_type, (model, field, target_model, label) in ASSIGNMENT_MODELS.items():
        for assignment, user, target in session.execute(select(model, User, target_model).join(User, model.user_id == User.id).join(target_model, getattr(model, field) == target_model.id)).all():
            target_name = getattr(target, "name", None) or getattr(target, "title", None)
            records.append({"user_id": str(user.id), "user_name": user.name, "target_type": target_type.value, "target_id": str(target.id), "target_name": target_name, "target_label": label, "assigned_at": assignment.created_at.isoformat()})
    return sorted(records, key=lambda item: (item["user_name"].lower(), item["target_type"], item["target_name"].lower()))


@router.get("/assignments")
def list_assignments(session: Session = Depends(get_db_session), _: AuthenticatedUser = admin_only):
    return assignment_records(session)


@router.post("/assignments", status_code=201)
def create_assignment(payload: AssignmentWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    entity(session, User, payload.user_id)
    model, field, target_model, label = ASSIGNMENT_MODELS[payload.target_type]
    entity(session, target_model, payload.target_id)
    existing = session.scalar(select(model).where(model.user_id == payload.user_id, getattr(model, field) == payload.target_id))
    if existing:
        raise HTTPException(status_code=409, detail="This assignment already exists")
    assignment = model(user_id=payload.user_id, **{field: payload.target_id})
    session.add(assignment); session.flush()
    log_admin_action(session, actor.id, "ASSIGN_LEARNING_CONTENT", label, payload.target_id, {"user_id": str(payload.user_id), "target_type": payload.target_type.value})
    session.commit()
    return {"user_id": str(payload.user_id), "target_type": payload.target_type.value, "target_id": str(payload.target_id)}


@router.delete("/assignments/{target_type}/{user_id}/{target_id}", status_code=204)
def delete_assignment(target_type: AssignmentTarget, user_id: uuid.UUID, target_id: uuid.UUID, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    model, field, _, label = ASSIGNMENT_MODELS[target_type]
    assignment = session.scalar(select(model).where(model.user_id == user_id, getattr(model, field) == target_id))
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    session.delete(assignment); session.flush()
    log_admin_action(session, actor.id, "REMOVE_LEARNING_ASSIGNMENT", label, target_id, {"user_id": str(user_id), "target_type": target_type.value})
    session.commit()
    return None


@router.get("/prerequisites")
def list_prerequisites(session: Session = Depends(get_db_session), _: AuthenticatedUser = admin_only):
    prerequisite = aliased(Course)
    rows = session.execute(
        select(CoursePrerequisite, Course, prerequisite)
        .join(Course, CoursePrerequisite.course_id == Course.id)
        .join(prerequisite, CoursePrerequisite.prerequisite_course_id == prerequisite.id)
    ).all()
    return [{"course_id": str(course.id), "course_title": course.title, "prerequisite_course_id": str(required.id), "prerequisite_course_title": required.title} for _, course, required in rows]


def would_create_prerequisite_cycle(session: Session, course_id: uuid.UUID, prerequisite_id: uuid.UUID) -> bool:
    pending = [prerequisite_id]
    visited = set()
    while pending:
        current = pending.pop()
        if current == course_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        pending.extend(session.scalars(select(CoursePrerequisite.prerequisite_course_id).where(CoursePrerequisite.course_id == current)).all())
    return False


@router.post("/prerequisites", status_code=201)
def create_prerequisite(payload: PrerequisiteWrite, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    entity(session, Course, payload.course_id); entity(session, Course, payload.prerequisite_course_id)
    if payload.course_id == payload.prerequisite_course_id or would_create_prerequisite_cycle(session, payload.course_id, payload.prerequisite_course_id):
        raise HTTPException(status_code=422, detail="A prerequisite cannot create a circular course dependency")
    if session.get(CoursePrerequisite, {"course_id": payload.course_id, "prerequisite_course_id": payload.prerequisite_course_id}):
        raise HTTPException(status_code=409, detail="This prerequisite already exists")
    session.add(CoursePrerequisite(**payload.model_dump())); session.flush()
    log_admin_action(session, actor.id, "ADD_COURSE_PREREQUISITE", "course", payload.course_id, {"prerequisite_course_id": str(payload.prerequisite_course_id)})
    session.commit()
    return {"course_id": str(payload.course_id), "prerequisite_course_id": str(payload.prerequisite_course_id)}


@router.delete("/prerequisites/{course_id}/{prerequisite_course_id}", status_code=204)
def delete_prerequisite(course_id: uuid.UUID, prerequisite_course_id: uuid.UUID, session: Session = Depends(get_db_session), actor: AuthenticatedUser = admin_only):
    record = session.get(CoursePrerequisite, {"course_id": course_id, "prerequisite_course_id": prerequisite_course_id})
    if record is None:
        raise HTTPException(status_code=404, detail="Prerequisite not found")
    session.delete(record); session.flush()
    log_admin_action(session, actor.id, "REMOVE_COURSE_PREREQUISITE", "course", course_id, {"prerequisite_course_id": str(prerequisite_course_id)})
    session.commit()
    return None

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
