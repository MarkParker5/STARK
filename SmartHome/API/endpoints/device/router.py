from uuid import UUID
from fastapi import APIRouter, Depends
from API import exceptions
from .DevicesManager import DevicesManager
from .schemas import Device, DeviceState, CreateDevice, PatchDevice


router = APIRouter(
    prefix = '/device',
    tags = ['device'],
)

@router.post('', response_model = Device)
async def create_device(device: CreateDevice, manager: DevicesManager = Depends()):
    return await manager.create(device)

@router.get('/{id}', response_model = DeviceState)
async def get_device(id: UUID, manager: DevicesManager = Depends()):
    if device := await manager.state(id):
        return device
    else:
        raise exceptions.not_found

@router.patch('/{id}')
async def patch_device(id: UUID, device: PatchDevice, manager: DevicesManager = Depends()):
    await manager.patch(id, device)

@router.delete('/{id}')
async def delete_device(id: UUID, manager: DevicesManager = Depends()):
    await manager.delete(id)
