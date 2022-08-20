from tests.setup import *


id = uuid1()
default_name = 'Inited Hub'
hub_init_json = {
    'id': str(id),
    'name': default_name,
    'house_id': str(faker.house_id),
    'access_token': hub_access_token,
    'refresh_token': hub_refresh_token,
    'public_key': public_key,
}

def test_get_hub_401():
    response = client.get('/api/hub')
    assert response.status_code in [401, 403], response.text
    assert response.json() in [{'detail': 'Not authenticated'}, {'detail': 'Access denied'}]

def test_init_hub_401():
    response = client.post('/api/hub', json = hub_init_json)
    assert response.status_code == 401, response.text
    assert response.json() == {'detail': 'Not authenticated'}

def _test_get_hub_404():
    response = client.get('/api/hub', headers = auth_headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

def test_init_hub():
    response = client.post('/api/hub', json = hub_init_json, headers = auth_headers)
    assert response.status_code == 200

def test_get_hub():
    response = client.get('/api/hub', headers = auth_headers)
    assert response.status_code == 200
    assert response.json() == {
        'id': str(id),
        'name': default_name,
        'house_id': str(faker.house_id),
    }

def test_patch_hub():
    hub = client.get('/api/hub', headers = auth_headers).json()
    hub['name'] = 'Patched Hub'

    response = client.patch('/api/hub', json = {
        'name': 'Patched Hub',
    }, headers = auth_headers)

    assert response.status_code == 200
    assert client.get('/api/hub', headers = auth_headers).json() == hub
