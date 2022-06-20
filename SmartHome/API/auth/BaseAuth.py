import time
from abc import ABC, abstractmethod
from uuid import UUID
from enum import Enum

from pydantic import BaseModel
from jose import jwt, JWTError

import config
import exceptions


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
    def get_tokens_pair(self, user_id: UUID, is_admin: bool) -> (str, str):
        pass

    @abstractmethod
    def _get_token(self, payload: dict) -> BaseToken:
        pass

    def validate_refresh(self, token: str) -> BaseToken:
        if (token := self._validate_token(token)) and self._is_refresh_valid(token):
            return token
        raise exceptions.invalid_token

    def validate_access(self, token: str) -> BaseToken:
        if (token := self._validate_token(token)) and self._is_access_valid(token):
            return token
        raise exceptions.invalid_token

    def _validate_token(self, token: str) -> BaseToken:
        try:
            payload = jwt.decode(token, config.public_key, algorithms=[config.algorithm])
            token = self._get_token(payload)
        except JWTError as e:
            raise exceptions.invalid_token

        if not token or not self._is_valid_token(token):
            raise exceptions.invalid_token

        return token

    def _is_access_valid(self, token: BaseToken) -> bool:
        return token.type == TokenType.access

    def _is_refresh_valid(self, token: BaseToken) -> bool:
        return token.type == TokenType.refresh

    def _is_valid_token(self, token: BaseToken) -> bool:
        return time.time() <= token.exp
