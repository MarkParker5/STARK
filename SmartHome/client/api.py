from typing import Type
from aiohttp import ClientSession
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
import config


headers = {'Auth': f'Bearer {config.access_token}'}

async def get(url: str,
              model: Type[BaseModel],
              client_session: ClientSession = None) -> BaseModel | None:
    try:
        session = client_session or ClientSession()
        async with session.get(f'{config.api_url}/{url}') as response:
            text = await response.text()
            return model.parse_raw(text)
    except ValidationError:
        print(f'\nAPI Error: {url}\nModel: {model}\n{text}\n')
        return None
    finally:
        if not client_session:
            await session.close()
        response.close()
