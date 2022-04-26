from uuid import UUID
from fastapi import APIRouter, Depends
from Controls.API import exceptions
from .DevicesManager import DevicesManager
from .schemas import Device, CreateDevice, PatchDevice


router = APIRouter(
    prefix = '/device',
    tags = ['device'],
)

@router.get('/{id}', response_model = Device)
async def device_get(id: UUID, manager: DevicesManager = Depends()):
    device = manager.get(id)

    if not device:
        raise exceptions.not_found

    return device

@router.post('', response_model = Device)
async def device_create(device: CreateDevice, manager: DevicesManager = Depends()):
    return manager.create(device)

@router.put('')
async def device_put(device: Device, manager: DevicesManager = Depends()):
    manager.update(device)

@router.patch('/{id}')
async def device_patch(id: UUID, device: PatchDevice, manager: DevicesManager = Depends()):
    manager.patch(id, device)

@router.delete('/{id}')
async def device_delete(id: UUID, manager: DevicesManager = Depends()):
    manager.delete(id)
