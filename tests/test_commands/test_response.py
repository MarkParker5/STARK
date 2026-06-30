from stark.core import Response


def test_response():
    response = Response("hello!")
    assert response.text == "hello!"
    assert response.voice == response.text
