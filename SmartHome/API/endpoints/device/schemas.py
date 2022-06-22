from uuid import UUID
from pydantic import BaseModel
from ..schemas import DeviceModel, DeviceParameter
from typing import Optional


class PatchDevice(BaseModel):
    name: str
    room_id: UUID

class CreateDevice(PatchDevice):
    id: UUID
    model_id: UUID

class Device(CreateDevice):
    model: DeviceModel

    class Config:
        orm_mode = True

class DeviceState(Device):
    parameters: list[DeviceParameter] = []
