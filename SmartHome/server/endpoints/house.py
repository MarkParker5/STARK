from uuid import UUID
from fastapi import APIRouter, Depends
from managers import HouseManager
from schemas.house import House
from server.dependencies.database import get_async_session, AsyncSession
from server.dependencies.auth import validate_user


router = APIRouter(
    prefix = '/house',
    tags = ['house'],
)

# MARK: - dependencies

async def session(session = Depends(get_async_session),
                  user = Depends(validate_user)) -> AsyncSession:
    return session

# MARK: - endpoints

@router.get('', response_model = House)
async def get_house(session = Depends(session)):
    manager = HouseManager(session)
    return await manager.get()
