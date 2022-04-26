from uuid import UUID
from fastapi import APIRouter, Depends
import Controls.API.exceptions
from .HubManager import HubManager
from .schemas import Hub, PatchHub


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

@router.post('/wifi')
async def hub_wifi(ssid: str, password: str, manager: HubManager = Depends()):
    manager.wifi(ssid, password)
