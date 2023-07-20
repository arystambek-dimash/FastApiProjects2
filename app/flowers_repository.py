from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import Flower


class FlowerRequest(BaseModel):
    name: str
    count: int
    cost: float


class FlowerResponse(BaseModel):
    id: int
    name: str
    cost: float
    count: int


class FlowersRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Flower).all()

    @staticmethod
    def get_flower_by_id(db: Session, flower_id):
        return db.query(Flower).filter(Flower.id == flower_id).first()

    @staticmethod
    def create_flower(db: Session, flower: FlowerRequest):
        flower_db = Flower(name=flower.name, cost=flower.cost, count=flower.count)
        db.add(flower_db)
        db.commit()
        db.refresh(flower_db)
        return flower_db

