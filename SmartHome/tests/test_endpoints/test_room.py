from tests.setup import *


id = uuid1()
room = {
    'name': 'New Room',
    'devices': []
}

def test_get_room_null():
    response = client.get(f'/api/room/', headers = auth_headers)
    assert response.status_code == 405
    assert response.json() == {'detail': 'Method Not Allowed'}

def test_get_room_404():
    response = client.get(f'/api/room/{id}', headers = auth_headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

def test_delete_room_404():
    response = client.delete(f'/api/room/{id}', headers = auth_headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

def test_create_room():
    response = client.post(f'/api/room', json = room, headers = auth_headers)
    new_room = response.json()
    assert response.status_code == 200
    global id
    id = new_room.get('id')
    assert id
    room['id'] = id
    assert new_room == room

def test_get_room():
    response = client.get(f'/api/room/{id}', headers = auth_headers)
    assert response.status_code == 200
    assert response.json() == room

def test_patch_room():
    room['name'] = 'Patched Room'
    response = client.patch(f'/api/room/{id}', json = room, headers = auth_headers)
    assert response.status_code == 200
    assert client.get(f'/api/room/{id}', headers = auth_headers).json() == room

def test_delete_room():
    response = client.delete(f'/api/room/{id}', json = room, headers = auth_headers)
    assert response.status_code == 200

def test_get_deleted_room():
    test_get_room_404()
