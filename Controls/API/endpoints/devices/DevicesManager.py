from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete

from Controls.API.models import Device
from Controls.API.dependencies import database
from . import schemas


class DevicesManager:
    def __init__(self, session = Depends(database.get_session)):
        self.session = session

    def get(self, id: UUID) -> Device | None:
        db = self.session
        return db.get(Device, id)

    def create(self, create_device: schemas.CreateDevice) -> Device:
        db = self.session
        device = Device(name = create_device.name, house_id = create_device.house_id)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    def update(self, device: schemas.Device):
        db = self.session
        values = {key: value for key, value in device.dict().items() if key != 'id'}
        db.execute(Device.__table__.update().values(values).filter_by(id = device.id))
        db.commit()

    def patch(self, id: UUID, device: schemas.PatchDevice):
        db = self.session
        values = {key: value for key, value in device.dict().items() if key != 'id' and value != None}
        db.execute(Device.__table__.update().values(values).filter_by(id = id))
        db.commit()

    def delete(self, device_id: UUID):
        db = self.session
        device = self.get(device_id)
        if device and device.house.owner_id == self.owner_id:
            db.delete(device)
            db.commit()