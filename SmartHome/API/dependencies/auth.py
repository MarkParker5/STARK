from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from API import exceptions
from API.models import User
from ..auth import (
    UserToken,
    UserAuthManager,
    AuthException
)
from .database import get_async_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = '/api/user/login')
userAuthManager = UserAuthManager()

async def validate_user(token: str = Depends(oauth2_scheme), session = Depends(get_async_session)) -> User:
    try:
        token = userAuthManager.validate_access(token)
        user = await session.get(User, token.user_id)
        if not user:
            raise AuthException
        return user
    except AuthException:
        raise exceptions.access_denied

def validate_token(token: str = Depends(oauth2_scheme)) -> UserToken:
    try:
        return userAuthManager.validate_access(token)
    except AuthException:
        raise exceptions.access_denied

def optional_token(token: str = Depends(oauth2_scheme)) -> UserToken | None:
    try:
        return userAuthManager.validate_access(token)
    except AuthException:
        return None

def raw_token(token: str = Depends(oauth2_scheme)) -> str:
    return token
