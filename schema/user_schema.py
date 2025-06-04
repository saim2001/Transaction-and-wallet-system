import uuid
from pydantic import BaseModel, EmailStr, constr
from typing import Annotated

__all__ = [
    "UserCreateRequest",
    "UserResponse",
    "SignInRequest"
]


class UserCreateRequest(BaseModel):
    username: Annotated[str, constr(strip_whitespace=True, min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, constr(min_length=8, max_length=128)]

    class Config:
        str_strip_whitespace = True
        from_attributes = True

class SignInRequest(BaseModel):
    email: Annotated[str, constr(strip_whitespace=True, min_length=3, max_length=50)]
    password: Annotated[str, constr(min_length=8, max_length=128)]

    class Config:
        str_strip_whitespace = True


class UserResponse(BaseModel):

    id: uuid.UUID
    username: str
    email: EmailStr

    class Config:
        from_attributes = True