from datetime import datetime

from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    content: str = ""
    points: int = 10
    due_at: datetime | None = None


class AssignmentRead(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    points: int
    due_at: datetime | None

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: int
    answer_text: str


class SubmissionRead(BaseModel):
    id: int
    assignment_id: int
    cadet_id: int
    score_awarded: int

    class Config:
        from_attributes = True

