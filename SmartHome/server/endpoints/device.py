from uuid import UUID
from fastapi import APIRouter, Depends

from exceptions.Internal import InternalException, ExceptionCode
from managers import DevicesManager
from schemas.device import (
    Device,
    DeviceState,
    DeviceCreate,
    DevicePatch
)
from server.dependencies.database import get_async_session, AsyncSession
from server.dependencies.auth import validate_user


router = APIRouter(
    prefix = '/device',
    tags = ['device'],
)

# MARK: - dependencies

async def manager(session = Depends(get_async_session),
                  user = Depends(validate_user)) -> DevicesManager:
    return DevicesManager(session)

# MARK: - endpoints

@router.post('', response_model = Device)
async def create_device(device: DeviceCreate, manager = Depends(manager)):
    return await manager.create(device)

@router.get('/{id}', response_model = DeviceState)
async def get_device(id: UUID, manager = Depends(manager)):
    return await manager.state(id)

@router.patch('/{id}')
async def patch_device(id: UUID, device: DevicePatch, manager = Depends(manager)):
    await manager.patch(id, device)

@router.delete('/{id}')
async def delete_device(id: UUID, manager = Depends(manager)):
    await manager.delete(id)
