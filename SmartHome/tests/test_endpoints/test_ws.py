from tests.setup import *


def _test_ws(device_id: UUID, parameter_id: UUID, value: int):
    with client.websocket_connect('/ws') as ws:
        ws.send_json({
            'type': 'merlin',
            'data': {
                'device_id': str(device_id),
                'parameter_id': str(parameter_id),
                'value': value
            }
        }, mode='text')
