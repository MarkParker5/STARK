from uuid import UUID
from fastapi import APIRouter, Depends
import SmartHome.API.exceptions
from .HubManager import HubManager
from .schemas import Hub, PatchHub, TokensPair, Hotspot


router = APIRouter(
    prefix = '/hub',
    tags = ['hub'],
)

@router.get('', response_model = Hub)
async def hub_get(manager: HubManager = Depends()):
    return manager.get()

@router.post('', response_model = Hub)
async def hub_create(hub: Hub, manager: HubManager = Depends()):
    return manager.create(hub)

@router.patch('')
async def hub_patch(hub: PatchHub, manager: HubManager = Depends()):
    manager.patch(hub)

@router.post('/connect')
async def hub_connect(ssid: str, password: str, manager: HubManager = Depends()):
    manager.wifi(ssid, password)

@router.get('/hotspots')
async def hub_hotspots(manager: HubManager = Depends()):
    return manager.get_hotspots()

@router.post('/set_tokens')
async def set_tokens(tokens: TokensPair):
    manager.save_tokens(tokens)
