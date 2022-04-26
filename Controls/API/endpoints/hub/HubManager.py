from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete

from Controls.API.models import Hub
from Controls.API.dependencies import database
from . import schemas
from Raspberry import WiFi


class HubManager:
    def __init__(self, session = Depends(database.get_session)):
        self.session = session

    def get(self) -> Hub | None:
        db = self.session
        return db.query(Hub).one()

    def create(self, create_hub: schemas.Hub) -> Hub:
        db = self.session

        if hub := self.get():
            db.delete(hub)

        hub = Hub(id = create_hub.id, name = create_hub.name, house_id = create_hub.house_id)
        db.add(hub)
        db.commit()
        db.refresh(hub)

        return hub

    def patch(self, id: UUID, hub: schemas.PatchHub):
        db = self.session
        values = {key: value for key, value in hub.dict().items() if key != 'id' and value != None}
        db.execute(Hub.__table__.update().values(values).filter_by(id = id))
        db.commit()

    def wifi(self, ssid: str, password: str):
        WiFi.save_and_connect(ssid, password)

    def set_tokens(tokens_pair: schemas.TokensPair):
        with open(f'{path}/{resources}/access_token.txt', 'w') as f:
            f.write(tokens_pair.access_token)
        with open(f'{path}/{resources}/refresh_token.txt', 'w') as f:
            f.write(tokens_pair.refresh_token)
