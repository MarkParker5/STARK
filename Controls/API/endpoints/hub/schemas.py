from uuid import UUID
from pydantic import BaseModel


class PatchHub(BaseModel):
    name: str

class Hub(BaseModel):
    id: UUID
    name: str
    house_id: UUID

    class Config:
        orm_mode = True
