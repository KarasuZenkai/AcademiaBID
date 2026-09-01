from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    LEARNER = "LEARNER"


class LessonType(str, Enum):
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    QUIZ = "QUIZ"
    LINK = "LINK"


class ProgressStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
