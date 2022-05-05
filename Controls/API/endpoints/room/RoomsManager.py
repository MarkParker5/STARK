from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete

from Controls.API.models import Room
from Controls.API.dependencies import database
from . import schemas


class RoomsManager:
    def __init__(self, session = Depends(database.get_session)):
        self.session = session

    def get(self, id: UUID) -> Room | None:
        db = self.session
        return db.get(Room, id)

    def create(self, create_room: schemas.PatchRoom) -> Room:
        db = self.session
        room = Room(name = create_room.name, house_id = create_room.house_id)
        db.add(room)
        db.commit()
        db.refresh(room)
        return room

    def update(self, room: schemas.Room):
        db = self.session
        values = {key: value for key, value in room.dict().items() if key != 'id'}
        db.execute(Room.__table__.update().values(values).filter_by(id = room.id))
        db.commit()

    def patch(self, id: UUID, room: schemas.PatchRoom):
        db = self.session
        values = {key: value for key, value in room.dict().items() if key != 'id' and value != None}
        db.execute(Room.__table__.update().values(values).filter_by(id = id))
        db.commit()

    def delete(self, room_id: UUID):
        db = self.session
        room = self.get(room_id)
        if room and room.house.owner_id == self.owner_id:
            db.delete(room)
            db.commit()
