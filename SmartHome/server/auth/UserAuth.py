import time
from uuid import UUID
from datetime import timedelta
from jose import jwt
import config
from .BaseAuth import BaseAuthManager, BaseToken, TokenType


class UserToken(BaseToken):
    user_id: UUID
    is_admin: bool

class UserAuthManager(BaseAuthManager):

    # abstract impl
    def _get_parsed_token(self, payload: dict) -> UserToken:
        return UserToken(**payload)

    # override
    def _is_valid_token(self, token: UserToken) -> bool:
        return super()._is_valid_token(token) and token.user_id != None
