from pydantic import BaseModel
from attrs import define


@define
class Flower(BaseModel):
    name: str
    count: int
    cost: float
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]
    carts: list[int]

    def __init__(self):
        self.flowers = [Flower(name="Roza", count=1, cost=float(5), id=1),
                        Flower(name="Roza", count=1, cost=float(5), id=2),
                        Flower(name="Roza", count=1, cost=float(5), id=3)]
        self.carts = []

    def get_all(self):
        return self.flowers

    def save(self, flower):
        if flower.id == 0:
            flower.id = self.get_next_id()
        self.flowers.append(flower)

    def get_next_id(self):
        return len(self.flowers) + 1

    def save_flower_to_cart(self, flower_id):
        self.carts.append(flower_id)

    def get_all_in_cart(self):
        return self.carts

    def get_by_id(self, flower_id):
        cart_flowers = []
        for i, f in enumerate(self.flowers):
            if f.id == flower_id:
                return self.flowers[i]

        return None
