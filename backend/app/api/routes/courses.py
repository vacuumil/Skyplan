import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.course import Course, CourseMembership
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.course import CourseCreate, CourseRead, JoinCourseRequest

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseRead)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    instructor: User = Depends(require_role(UserRole.instructor)),
):
    course = Course(
        title=payload.title,
        description=payload.description,
        instructor_id=instructor.id,
        invite_code=secrets.token_urlsafe(8),
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.instructor, UserRole.cadet)),
):
    if user.role == UserRole.instructor:
        return db.scalars(select(Course).where(Course.instructor_id == user.id)).all()

    stmt = (
        select(Course)
        .join(CourseMembership, CourseMembership.course_id == Course.id)
        .where(CourseMembership.cadet_id == user.id)
    )
    return db.scalars(stmt).all()


@router.post("/join", response_model=CourseRead)
def join_course(
    payload: JoinCourseRequest,
    db: Session = Depends(get_db),
    cadet: User = Depends(require_role(UserRole.cadet)),
):
    course = db.scalar(select(Course).where(Course.invite_code == payload.invite_code))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = db.scalar(
        select(CourseMembership).where(
            CourseMembership.course_id == course.id,
            CourseMembership.cadet_id == cadet.id,
        )
    )
    if existing:
        return course

    membership = CourseMembership(course_id=course.id, cadet_id=cadet.id)
    db.add(membership)
    db.commit()
    return course

