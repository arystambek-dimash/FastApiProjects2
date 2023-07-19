from pydantic import BaseModel
from attrs import define


@define
class Flower(BaseModel):
    name: str
    count: int
    cost: float
    id: int = 0


class FlowersRepository:
    pass
