from uuid import UUID
from pydantic import BaseModel
from ..schemas import DeviceModel, DeviceParameter
from typing import Optional

class CreateDevice(BaseModel):
    name: str

class PatchDevice(BaseModel):
    name: str | None

class Device(BaseModel):
    id: UUID
    name: str
    model: DeviceModel

    class Config:
        orm_mode = True

class DeviceState(Device):
    parameters: list[DeviceParameter] = []
