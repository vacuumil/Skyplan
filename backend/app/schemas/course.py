from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str
    description: str = ""


class CourseRead(BaseModel):
    id: int
    title: str
    description: str
    invite_code: str
    instructor_id: int

    class Config:
        from_attributes = True


class JoinCourseRequest(BaseModel):
    invite_code: str

