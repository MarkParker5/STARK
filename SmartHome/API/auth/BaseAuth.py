import time
from abc import ABC, abstractmethod
from uuid import UUID
from enum import Enum

from pydantic import BaseModel
from jose import jwt, JWTError
from jose.exceptions import JWKError

import config
from .exceptions import AuthException


class TokenType(str, Enum):
    access = 'access'
    refresh = 'refresh'

class TokensPair(BaseModel):
    access_token: str
    refresh_token: str

class HubAuthItem(TokensPair):
    public_key: str

class BaseToken(BaseModel):
    type: TokenType
    exp: float

class BaseAuthManager(ABC):

    @abstractmethod
    def _get_parsed_token(self, payload: dict) -> BaseToken:
        pass

    def validate_access(self, token: str) -> BaseToken:
        token = self._parse_token(token)

        if not token:
            raise AuthException()

        if token.type != TokenType.access:
            raise AuthException()

        if not self._is_valid_token(token):
            raise AuthException()

        return token

    def _parse_token(self, token: str) -> BaseToken:
        try:
            payload = jwt.decode(token, config.public_key, algorithms = [config.algorithm])
            token = self._get_parsed_token(payload)
        except JWTError:
            raise AuthException()
        except JWKError:
            raise AuthException()
        return token

    def _is_valid_token(self, token: BaseToken) -> bool:
        return time.time() <= token.exp
