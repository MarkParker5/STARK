from tests.setup import *


id = uuid1()
default_name = 'Inited Hub'

# def test_get_hub_404():
#     response = client.get('/api/hub')
#     assert response.status_code == 404
#     assert response.json() == {'detail': 'Not found'}

def test_init_hub():
    response = client.post('/api/hub', json = {
        'id': str(id),
        'name': default_name,
        'house_id': str(house_id),
        'access_token': hub_access_token,
        'refresh_token': hub_refresh_token,
        'public_key': public_key,
    })
    assert response.status_code == 200

def test_get_hub():
    response = client.get('/api/hub')
    assert response.status_code == 200
    assert response.json() == {
        'id': str(id),
        'name': default_name,
        'house_id': str(house_id),
    }

def test_patch_hub():
    hub = client.get('/api/hub').json()
    hub['name'] = 'Patched Hub'

    response = client.patch('/api/hub', json = {
        'name': 'Patched Hub',
    })

    assert response.status_code == 200
    assert client.get('/api/hub').json() == hub
