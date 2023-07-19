from attrs import define
from pydantic import BaseModel, Field, EmailStr
from fastapi import HTTPException


@define
class UserRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str = Field(min_length=8)
    id: int = 0


@define
class UserResponse(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    id: int = 0


class UsersRepository:
    pass