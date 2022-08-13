from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from AUID import AUID
from ..schemas import DeviceModel, DeviceParameter


class PatchDevice(BaseModel):
    name: str
    room_id: UUID

class CreateDevice(PatchDevice):
    id: AUID

class Device(CreateDevice):
    model: DeviceModel

    class Config:
        orm_mode = True

class DeviceState(Device):
    parameters: list[DeviceParameter] = []
