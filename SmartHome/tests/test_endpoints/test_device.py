from tests.setup import *


faker.init_hub()
id = uuid1()
room_id = faker.create_room().id
model_id = faker.create_device_model().id
device = {
    'id': str(id),
    'name': 'New Room',
    'room_id': str(room_id),
    'model_id': str(model_id),
}

def test_get_device_null():
    response = client.get(f'/api/device/', headers = auth_headers)
    assert response.status_code == 405
    assert response.json() == {'detail': 'Method Not Allowed'}

def test_get_device_404():
    response = client.get(f'/api/device/{id}', headers = auth_headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

def test_delete_device_404():
    response = client.delete(f'/api/device/{id}', headers = auth_headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

def test_create_device():
    response = client.post(f'/api/device', json = device, headers = auth_headers)
    new_device = response.json()
    assert response.status_code == 200
    assert new_device.get('model')
    device['model'] = new_device.get('model')
    assert new_device == device

def test_get_device():
    response = client.get(f'/api/device/{id}', headers = auth_headers)
    device['parameters'] = []
    assert response.status_code == 200
    assert response.json() == device

def test_patch_device():
    device['name'] = 'Patched Device'
    response = client.patch(f'/api/device/{id}', json = device, headers = auth_headers)
    assert response.status_code == 200
    assert client.get(f'/api/device/{id}', headers = auth_headers).json() == device

def test_delete_device():
    response = client.delete(f'/api/device/{id}', json = device, headers = auth_headers)
    assert response.status_code == 200

def test_get_deleted_device():
    test_get_device_404()
