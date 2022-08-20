from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from exceptions.Internal import InternalException, ExceptionCode
from models import User
from ..auth import (
    UserToken,
    UserAuthManager,
    AuthException
)
from .database import get_async_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = '/api/user/login')
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl = '/api/user/login', auto_error=False)
userAuthManager = UserAuthManager()

async def validate_user(raw_token: str = Depends(oauth2_scheme), session = Depends(get_async_session)) -> User:
    token = userAuthManager.validate_access(raw_token)
    user = await session.get(User, token.user_id)
    if not user:
        raise AuthException()
    return user

def validate_token(token: str = Depends(oauth2_scheme)) -> UserToken:
    return userAuthManager.validate_access(token)

def optional_token(token: str = Depends(optional_oauth2_scheme)) -> UserToken | None:
    if not token:
        return None
    try:
        return userAuthManager.validate_access(token)
    except AuthException:
        return None

def raw_token(token: str = Depends(oauth2_scheme)) -> str:
    return token
