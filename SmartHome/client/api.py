from typing import Type
from aiohttp import ClientSession
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from schemas.ws import RestRequest
import config


headers = {'Authorization': f'Bearer {config.access_token}'}
client_session: ClientSession = None

async def start_client():
    global client_session
    if client_session:
        client_session.close()
    client_session = ClientSession()

async def get(url: str,
              model: Type[BaseModel]) -> BaseModel | None:
    try:
        async with client_session.get(f'{config.api_url}/{url}') as response:
            text = await response.text()
            return model.parse_raw(text)
    except ValidationError:
        print(f'\nAPI ValidationError Error: {url}\nModel: {model}\n{text}\n')
        return None

async def local_request(request: RestRequest) -> str:
    method = getattr(client_session, request.method)

    url = f'{config.localhost}/{request.path}'
    json = request.body
    headers = {}

    async with method(url, json = json, headers = headers) as r:
        if 200 <= response.status < 300:
            return await response.text()
