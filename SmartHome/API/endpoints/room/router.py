from uuid import UUID
from fastapi import APIRouter, Depends
from API import exceptions
from .RoomsManager import RoomsManager
from .schemas import Room, CreateRoom, PatchRoom


router = APIRouter(
    prefix = '/room',
    tags = ['room'],
)

@router.post('', response_model = Room)
async def create_room(room: CreateRoom, manager: RoomsManager = Depends()):
    return await manager.create(room)

@router.get('/{id}', response_model = Room)
async def get_room(id: UUID, manager: RoomsManager = Depends()):
    room = await manager.get(id)
    if not room:
        raise exceptions.not_found
    return room

@router.patch('/{id}')
async def patch_room(id: UUID, room: PatchRoom, manager: RoomsManager = Depends()):
    await manager.patch(id, room)

@router.delete('/{id}')
async def delete_room(id: UUID, manager: RoomsManager = Depends()):
    await manager.delete(id)
