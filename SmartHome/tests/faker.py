from uuid import UUID, uuid1
from typing import Callable, Any
import random

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from API import models


room_names = [ 'Atrium', 'Ballroom', 'Bathroom', 'Bedroom', 'Billiard room', 'Cabinet', 'Computer lab',
  'Conference hall', 'Control room', 'Corner office', 'Dining room', 'Drawing room', 'Office',
  'Roomsharing', 'Root cellar', 'Rotting room', 'Rotunda', 'Small office', 'Student lounge',
  'Studio', 'Sunroom', 'Throne room', 'Toolroom', 'Waiting room', 'Workshop']
model_names = ['Lamp', 'Led', 'Light', 'Lock', 'Door', 'Window rollets', 'Cleaner', 'TV', 'Speaker', 'Spot']
parameter_names = ['Is on', 'Color', 'Power', 'Brightness', 'Mode', 'Target', 'Timer', 'Volume', 'Channel']
parameter_value_types = ['bool', 'decimal', 'enum']

class Faker:
    client: TestClient
    create_session: Callable[[], Session]

    house_id = uuid1()

    # inject
    hub_access_token: str = ''
    hub_refresh_token: str = ''
    public_key: str = ''

    def __init__(self, client: TestClient, create_session: Callable[[], Session]):
        self.client = client
        self.create_session = create_session

    def init_hub(self):
        hub_id = uuid1()
        default_name = 'Inited Hub'

        response = self.client.post('/api/hub', json = {
            'id': str(hub_id),
            'name': default_name,
            'house_id': str(self.house_id),
            'access_token': self.hub_access_token,
            'refresh_token': self.hub_refresh_token,
            'public_key': self.public_key,
        })
        assert response.status_code == 200, f'{response.status_code}{response.text}'
        return response.json()

    def get_house(self) -> dict[str, Any]:
        response = self.client.get(f'/api/house/')
        assert response.status_code == 200
        return response.json()

    def create_room(self):
        with self.create_session() as session:
            room = models.Room(house_id = self.house_id, name = random.choice(room_names))
            session.add(room)
            session.commit()
            session.refresh(room)
            return room

    def create_device_model(self) -> models.DeviceModel:
        with self.create_session() as session:
            device_model = models.DeviceModel(name = random.choice(model_names))
            session.add(device_model)
            session.commit()
            session.refresh(device_model)
            return device_model

    def create_parameter(self) -> models.Parameter:
        with self.create_session() as session:
            parameter = models.Parameter(name = random.choice(parameter_names),
                                        value_type = random.choice(parameter_value_types))
            session.add(parameter)
            session.commit()
            session.refresh(parameter)
            return parameter

    def create_device(self, name: str, room_id: UUID, model_id: UUID) -> models.Device:
        with self.create_session() as session:
            device = models.Device(
                name = name,
                urdi = random.randint(0, 2**32),
                room_id = room_id,
                model_id = model_id,
            )
            session.add(device)
            session.commit()
            session.refresh(device)
            return device

    def associate_devicemodel_parameter(self,
                                         devicemodel_id: UUID,
                                         parameter_id: UUID,
                                         f: int) -> models.DeviceModelParameter:

        with self.create_session() as session:
            parameter = models.DeviceModelParameter(
                devicemodel_id = devicemodel_id,
                parameter_id = parameter_id,
                f = f
            )
            session.add(parameter)
            session.commit()
            session.refresh(parameter)
            return parameter

    def fill_db(self) -> models.House:
        self.init_hub()

        with self.create_session() as session:
            house = session.get(models.House, self.house_id)

        device_models = [self.create_device_model() for _ in range(7)]
        parameters = [self.create_parameter() for _ in range(14)]

        for model in device_models:
            random.shuffle(parameters)
            for i in range(random.randint(1, 9)):
                parameter = parameters[i]
                self.associate_devicemodel_parameter(
                    model.id, parameter.id, i
                )

        for r in range(5):
            room = self.create_room()
            house.rooms.append(room)
            for d in range(5):
                device_model = random.choice(device_models)
                name = f'{device_model.name} in {room.name.lower()}'
                device = self.create_device(name, room.id, device_model.id)

        return house
