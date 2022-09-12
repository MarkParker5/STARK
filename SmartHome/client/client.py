import asyncio
from exceptions.Internal import InternalException
from schemas.hub import HubPatch
from schemas.house import HousePatch
from schemas.device import DeviceModelInfo
from managers import HubManager, HouseManager, DeviceModelManager
from database import create_async_session, AsyncSession
from . import api


def fetch():
    asyncio.run(fetch_all())

async def fetch_all():
    await api.start_client()
    async with create_async_session() as session:
        await asyncio.gather(
            fetch_house(session),
            fetch_hub(session),
            fetch_device_models(session)
        )

async def fetch_house(session: AsyncSession):
    manager = HouseManager(session)
    try:
        house = await manager.get()
    except InternalException:
        return
    if patch_house := await api.get(f'house/{house.id}', HousePatch):
        await manager.patch(patch_house)

async def fetch_hub(session: AsyncSession):
    manager = HubManager(session)
    try:
        hub = await manager.get()
    except InternalException:
        return
    if patch_hub := await api.get(f'hub/{hub.id}', HubPatch):
        await manager.patch(patch_hub)

async def fetch_device_models(session: AsyncSession):
    manager = DeviceModelManager(session)
    if devicemodels := await api.get(f'device_model', DeviceModelInfo):
        print(devicemodels)
        for devicemodel in devicemodels:
            manager.save(devicemodel)
