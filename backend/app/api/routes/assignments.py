from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.assignment import Assignment, Submission
from app.models.course import Course, CourseMembership
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentRead,
    SubmissionCreate,
    SubmissionRead,
)

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("", response_model=AssignmentRead)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_role(UserRole.instructor)),
):
    course = db.get(Course, payload.course_id)
    if not course or course.instructor_id != instructor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    assignment = Assignment(
        course_id=payload.course_id,
        title=payload.title,
        content=payload.content,
        points=payload.points,
        due_at=payload.due_at,
        created_by_id=instructor.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/my", response_model=list[AssignmentRead])
def my_assignments(
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.instructor, UserRole.cadet)),
):
    if user.role == UserRole.instructor:
        stmt = (
            select(Assignment)
            .join(Course, Course.id == Assignment.course_id)
            .where(Course.instructor_id == user.id)
        )
        return db.scalars(stmt).all()

    stmt = (
        select(Assignment)
        .join(Course, Course.id == Assignment.course_id)
        .join(CourseMembership, CourseMembership.course_id == Course.id)
        .where(CourseMembership.cadet_id == user.id)
    )
    return db.scalars(stmt).all()


@router.post("/submit", response_model=SubmissionRead)
def submit_assignment(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    cadet: User = Depends(require_role(UserRole.cadet)),
):
    assignment = db.get(Assignment, payload.assignment_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    membership = db.scalar(
        select(CourseMembership).where(
            CourseMembership.course_id == assignment.course_id,
            CourseMembership.cadet_id == cadet.id,
        )
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to course")

    submission = Submission(
        assignment_id=payload.assignment_id,
        cadet_id=cadet.id,
        answer_text=payload.answer_text,
        score_awarded=0,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

