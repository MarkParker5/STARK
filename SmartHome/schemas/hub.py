from uuid import UUID
from pydantic import BaseModel


# Auth

class TokensPair(BaseModel):
    access_token: str
    refresh_token: str

class HubAuthItems(TokensPair):
    public_key: str

# Hub

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

# WiFi

class Hotspot(BaseModel):
    ssid: str
    quality: float
    frequency: str
    encrypted: bool
    #encryption_type: str

    class Config:
        orm_mode = True

class WifiConnection(BaseModel):
    ssid: str
    password: str
