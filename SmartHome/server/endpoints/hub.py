from fastapi import APIRouter, Depends, BackgroundTasks
from managers import HubManager
from schemas.hub import (
    HubInit,
    Hub,
    HubPatch,
    TokensPair,
    Hotspot,
    WifiConnection
)
from server.dependencies.database import get_async_session, AsyncSession
from server.dependencies.auth import validate_user, raw_token


router = APIRouter(
    prefix = '/hub',
    tags = ['hub'],
)

# MARK: - dependencies

async def manager(session = Depends(get_async_session)) -> HubManager:
    return HubManager(session)

async def manager_auth(manager = Depends(manager),
                  user = Depends(validate_user)) -> HubManager:
    return manager

# MARK: - endpoints

@router.post('', response_model = Hub)
async def init_hub(hub_init: HubInit,
                   manager = Depends(manager),
                   raw_token: str = Depends(raw_token)):
    return await manager.init(hub_init, raw_token)

@router.get('', response_model = Hub)
async def get_hub(manager = Depends(manager_auth)):
    return await manager.get()

@router.patch('')
async def patch_hub(hub: HubPatch, manager = Depends(manager_auth)):
    await manager.patch(hub)

@router.post('/connect')
async def connect_to_wifi(wifi: WifiConnection, manager = Depends(manager_auth)):
    manager.wifi(wifi.ssid, wifi.password)

@router.get('/hotspots', response_model = list[Hotspot])
def get_hub_hotspots(manager = Depends(manager_auth)):
    return manager.get_hotspots()

@router.get('/is_connected', response_model=bool)
def is_connected(bg_tasks: BackgroundTasks, manager = Depends(manager_auth)):
    connected = manager.is_connected()
    if connected:
        bg_tasks.add_task(manager.stop_hotspot)
    return connected

@router.post('/set_tokens')
async def set_tokens(tokens: TokensPair, manager = Depends(manager_auth)):
    manager.save_tokens(tokens)
