from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String, index=True, default="user12345678")
    is_superuser = Column(Boolean, default=False)


class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cost = Column(Float)
    count = Column(Integer)


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,index=True)
    flower_id = Column(Integer)
