from tests.setup import *


def get_house() -> dict[str, Any]:
    response = client.get(f'/api/house/')
    assert response.status_code == 200
    return response.json()

def test_get_house():
    get_house()
