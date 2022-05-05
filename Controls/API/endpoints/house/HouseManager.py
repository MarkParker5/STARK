from uuid import UUID

from fastapi import Depends

from Controls.API.models import House
from Controls.API.dependencies import database
from . import schemas


class HouseManager:
    def __init__(self, session = Depends(database.get_session)):
        self.session = session

    def get(self) -> House:
        db = self.session
        return db.query(House).one()
