from fastapi import APIRouter, Depends, BackgroundTasks
from API import exceptions
from API.dependencies import auth
from .HubManager import HubManager
from .schemas import HubInit, Hub, HubPatch, TokensPair, Hotspot, WifiConnection


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
async def connect_to_wifi(wifi: WifiConnection, manager: HubManager = Depends()):
    await manager.check_access()
    manager.wifi(wifi.ssid, wifi.password)

@router.post('/wps')
async def start_wps(manager: HubManager = Depends()):
    await manager.check_access()
    manager.start_wps()

@router.get('/hotspots', response_model = list[Hotspot])
def get_hub_hotspots(manager: HubManager = Depends()):
    return manager.get_hotspots()

@router.get('/is-connected', response_model=bool)
def is_connected(bg_tasks: BackgroundTasks, manager: HubManager = Depends()):
    connected = manager.is_connected()
    if connected:
        bg_tasks.add_task(manager.stop_hotspot)
    return connected

@router.post('/set_tokens')
async def set_tokens(tokens: TokensPair, manager: HubManager = Depends()):
    await manager.check_access()
    manager.save_tokens(tokens)
