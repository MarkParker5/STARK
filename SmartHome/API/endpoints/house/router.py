from uuid import UUID
from fastapi import APIRouter, Depends
from SmartHome.API import exceptions
from .HouseManager import HouseManager
from .schemas import House


router = APIRouter(
    prefix = '/house',
    tags = ['house'],
)

@router.get('', response_model = House)
async def house_get(manager: HouseManager = Depends()):
    return manager.get()
