from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from AUID import AUID
from .parameters import DeviceParameter, Parameter


class DeviceModelInfo(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class DeviceModel(DeviceModelInfo):
    parameters: list[Parameter]

class DevicePatch(BaseModel):
    name: str
    room_id: UUID

class DeviceCreate(DevicePatch):
    id: AUID

class Device(DeviceCreate):
    model: DeviceModel

    class Config:
        orm_mode = True

class DeviceState(Device):
    parameters: list[DeviceParameter] = []
