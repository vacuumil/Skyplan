import enum


class UserRole(str, enum.Enum):
    instructor = "instructor"
    cadet = "cadet"

