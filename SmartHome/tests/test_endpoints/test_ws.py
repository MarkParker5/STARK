from starlette.websockets import WebSocketDisconnect
from tests.setup import *


def get_device() -> models.Device:
    with create_session() as session:
        return session.scalars(
            select(models.Device)
        ).first()

def _test_ws():
    faker.fill_db()
    device = get_device()
    parameter_id = device.model.parameters[0].parameter_id
    try:
        with client.websocket_connect('/ws/', headers = auth_headers) as ws:
            ws.send_json({
                'type': 'merlin',
                'data': {
                    'device_id': str(device.id),
                    'parameter_id': str(parameter_id),
                    'value': 0
                }
            }, mode = 'text')
    except WebSocketDisconnect:
        pass
