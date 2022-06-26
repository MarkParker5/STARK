from fastapi import APIRouter, Depends
from API import exceptions
from API.dependencies import auth
from .HubManager import HubManager
from .schemas import HubInit, Hub, HubPatch, TokensPair, Hotspot


router = APIRouter(
    prefix = '/hub',
    tags = ['hub'],
)

@router.post('', response_model = Hub)
async def init_hub(hub_init: HubInit, manager: HubManager = Depends(), raw_token: str = Depends(auth.raw_token)):
    manager.save_credentials(hub_init)
    await manager.parse_token(raw_token)
    return await manager.init(hub_init)

@router.get('', response_model = Hub)
async def get_hub(manager: HubManager = Depends()):
    await manager.check_access()
    hub = await manager.get()
    if hub:
        return hub
    raise exceptions.not_found

@router.patch('')
async def patch_hub(hub: HubPatch, manager: HubManager = Depends()):
    await manager.check_access()
    await manager.patch(hub)

@router.post('/connect')
async def connect_to_wifi(ssid: str, password: str, manager: HubManager = Depends()):
    await manager.check_access()
    await manager.wifi(ssid, password)

@router.get('/hotspots', response_model = list[Hotspot])
async def get_hub_hotspots(manager: HubManager = Depends()):
    await manager.check_access()
    return await manager.get_hotspots()

@router.post('/set_tokens')
async def set_tokens(tokens: TokensPair, manager: HubManager = Depends()):
    await manager.check_access()
    manager.save_tokens(tokens)
