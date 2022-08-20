from uuid import UUID
from fastapi import APIRouter, Depends
from managers import RoomsManager
from schemas.room import Room, RoomCreate, RoomPatch
from server.dependencies.database import get_async_session, AsyncSession
from server.dependencies.auth import validate_user, raw_token


router = APIRouter(
    prefix = '/room',
    tags = ['room'],
)

# MARK: - dependencies

async def manager(session = Depends(get_async_session),
                  user = Depends(validate_user)) -> RoomsManager:
    return RoomsManager(session)

# MARK: - endpoints

@router.post('', response_model = Room)
async def create_room(room: RoomCreate, manager = Depends(manager)):
    return await manager.create(room)

@router.get('/{id}', response_model = Room)
async def get_room(id: UUID, manager = Depends(manager)):
    return await manager.get(id)

@router.patch('/{id}')
async def patch_room(id: UUID, room: RoomPatch, manager = Depends(manager)):
    await manager.patch(id, room)

@router.delete('/{id}')
async def delete_room(id: UUID, manager = Depends(manager)):
    await manager.delete(id)
