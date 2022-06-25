from uuid import UUID
from pydantic import BaseModel


class Parameter(BaseModel):
    id: UUID
    name: str
    value_type: str

    class Config:
        orm_mode = True

class DeviceParameter(Parameter):
    value: int

class DeviceModel(BaseModel):
    id: UUID
    name: str
    parameters: list[Parameter]

    class Config:
        orm_mode = True
