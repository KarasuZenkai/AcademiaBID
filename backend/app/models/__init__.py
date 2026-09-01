"""Model registry used by Alembic."""

from app.models.catalog import Academy, Course, LearningPath, LearningPathCourse, Lesson, Module
from app.models.identity import Group, User
from app.models.progress import AuditLog, CourseCompletion, Enrollment, LearningPathCompletion, LessonProgress, QuizAttempt, VideoRange, VideoSession

__all__ = ["Academy", "AuditLog", "Course", "CourseCompletion", "Enrollment", "Group", "LearningPath", "LearningPathCompletion", "LearningPathCourse", "Lesson", "LessonProgress", "Module", "QuizAttempt", "User", "VideoRange", "VideoSession"]
