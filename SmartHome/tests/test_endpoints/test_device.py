from tests.setup import *


faker.init_hub()
id = '62ff3e2b-0130-0002-0001-000000000001'
room_id = faker.create_room().id
faker.create_device_model('00000000-0000-0002-0000-000000000000')
device = {
    'id': id,
    'name': 'New Room',
    'room_id': str(room_id),
}

def test_get_device_null():
    response = client.get(f'/api/device/', headers = auth_headers)
    assert response.status_code == 405, response.text
    assert response.json().get('detail') == 'Method Not Allowed'

def test_get_device_404():
    response = client.get(f'/api/device/{id}', headers = auth_headers)
    assert response.status_code == 404, response.text
    assert response.json().get('detail') == 'Device not found'

def test_delete_device_404():
    response = client.delete(f'/api/device/{id}', headers = auth_headers)
    assert response.status_code == 404, response.text
    assert response.json().get('detail') == 'Device not found'

def test_create_device():
    response = client.post(f'/api/device', json = device, headers = auth_headers)
    new_device = response.json()
    assert response.status_code == 200, response.text
    assert new_device.get('model')
    device['model'] = new_device.get('model')
    assert new_device == device

def test_get_device():
    response = client.get(f'/api/device/{id}', headers = auth_headers)
    device['parameters'] = []
    assert response.status_code == 200, response.text
    assert response.json() == device

def test_patch_device():
    device['name'] = 'Patched Device'
    response = client.patch(f'/api/device/{id}', json = device, headers = auth_headers)
    assert response.status_code == 200, response.text
    assert client.get(f'/api/device/{id}', headers = auth_headers).json() == device

def test_delete_device():
    response = client.delete(f'/api/device/{id}', json = device, headers = auth_headers)
    assert response.status_code == 200, response.text

def test_get_deleted_device():
    test_get_device_404()
