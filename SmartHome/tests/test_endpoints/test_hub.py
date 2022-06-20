from tests.setup import *


def test_init_hub():
    id = uuid1()
    house_id = uuid1()

    response = client.post('/api/hub', json = {
        'id': str(id),
        'name': 'Inited Hub',
        'house_id': str(house_id),
        'access_token': hub_access_token,
        'refresh_token': hub_refresh_token,
        'public_key': public_key,
    })

    assert response.status_code == 200

# Patch

def test_patch_hub():
    hub = client.get('/api/hub').json()
    hub['name'] = 'Patched Hub'

    response = client.patch('/api/hub', json = {
        'name': 'Patched Hub',
    })

    assert response.status_code == 200
    assert client.get('/api/hub').json() == hub
