from datetime import datetime

from pydantic import BaseModel, EmailStr


class EmployeeBase(BaseModel):

    first_name: str
    last_name: str
    email: EmailStr
    department: str
    designation: str


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):

    id: int
    profile_image_url: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True