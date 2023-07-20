from pydantic import BaseModel, Field,EmailStr
from sqlalchemy.orm import Session
from . import models


class UserRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id:int
    email: EmailStr
    username: str
    full_name: str


class UsersRepository:
    @staticmethod
    def get_user_by_username(db: Session, username):
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user: UserRequest) -> models.User:
        db_user = models.User(email=user.email, username=user.username, full_name=user.full_name,
                              password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
