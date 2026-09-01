"""Model registry used by Alembic."""

from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.identity import Group, User
from app.models.progress import AcademyAssignment, AuditLog, CourseCompletion, CoursePrerequisite, Enrollment, LearningPathAssignment, LearningPathCompletion, LessonProgress, ModuleAssignment, QuizAttempt, VideoRange, VideoSession

__all__ = ["Academy", "AcademyAssignment", "AuditLog", "Course", "CourseCompletion", "CoursePrerequisite", "Enrollment", "Group", "LearningPath", "LearningPathAssignment", "LearningPathCompletion", "LearningPathCourse", "Lesson", "LessonProgress", "Module", "ModuleAssignment", "QuizAttempt", "User", "VideoRange", "VideoSession"]
