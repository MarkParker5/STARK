from fastapi import APIRouter, Depends
from API import exceptions
from .HubManager import HubManager
from .schemas import HubInit, Hub, HubPatch, TokensPair, Hotspot


router = APIRouter(
    prefix = '/hub',
    tags = ['hub'],
)

@router.post('', response_model = Hub)
async def init_hub(hub: HubInit, manager: HubManager = Depends()):
    return await manager.init(hub)

@router.get('', response_model = Hub)
async def get_hub(manager: HubManager = Depends()):
    hub = await manager.get()
    if hub:
        return hub
    else:
        raise exceptions.not_found

@router.patch('')
async def patch_hub(hub: HubPatch, manager: HubManager = Depends()):
    await manager.patch(hub)

@router.post('/connect')
async def connect_to_hub(ssid: str, password: str, manager: HubManager = Depends()):
    manager.wifi(ssid, password)

@router.get('/hotspots', response_model = list[Hotspot])
async def get_hub_hotspots(manager: HubManager = Depends()):
    return manager.get_hotspots()

@router.post('/set_tokens')
async def set_tokens(tokens: TokensPair, manager: HubManager = Depends()):
    manager.save_tokens(tokens)
