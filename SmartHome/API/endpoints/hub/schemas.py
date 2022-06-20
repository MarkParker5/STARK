from uuid import UUID
from pydantic import BaseModel


class TokensPair(BaseModel):
    access_token: str
    refresh_token: str

class HubAuthItems(TokensPair):
    public_key: str

class Hub(BaseModel):
    id: UUID
    name: str
    house_id: UUID

    class Config:
        orm_mode = True

class HubPatch(BaseModel):
    name: str

class HubInit(Hub, HubAuthItems):
    ...

class Hotspot(BaseModel):
    ssid: str
