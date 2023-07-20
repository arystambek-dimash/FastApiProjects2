from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import Purchase


class PurchaseResponse(BaseModel):
    user_id: int
    flower_id: int


class PurchasesRepository:

    @staticmethod
    def get_all_user_purchases(db: Session, user_id):
        return db.query(Purchase).filter(Purchase.user_id == user_id)

    @staticmethod
    def save_purchases(db: Session, purchases: PurchaseResponse):
        db_purchases = Purchase(user_id=purchases.user_id, flower_id=purchases.flower_id)
        db.add(db_purchases)
        db.commit()
        db.refresh(db_purchases)
        return db_purchases
