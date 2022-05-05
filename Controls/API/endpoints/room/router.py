from uuid import UUID
from fastapi import APIRouter, Depends
from Controls.API import exceptions
from .RoomsManager import RoomsManager
from .schemas import Room, PatchRoom, PatchRoom


router = APIRouter(
    prefix = '/room',
    tags = ['room'],
)

@router.get('/{id}', response_model = Room)
async def room_get(id: UUID, manager: RoomsManager = Depends()):
    room = manager.get(id)

    if not room:
        raise exceptions.not_found

    return room

@router.post('', response_model = Room)
async def room_create(room: PatchRoom, manager: RoomsManager = Depends()):
    return manager.create(room)

@router.put('')
async def room_put(room: Room, manager: RoomsManager = Depends()):
    manager.update(room)

@router.patch('/{id}')
async def room_patch(id: UUID, room: PatchRoom, manager: RoomsManager = Depends()):
    manager.patch(id, room)

@router.delete('/{id}')
async def room_delete(id: UUID, manager: RoomsManager = Depends()):
    manager.delete(id)
