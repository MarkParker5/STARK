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

    def get_tokens_pair(self, user_id: UUID, is_admin: bool) -> (str, str):
        access_token = self._get_token_str(TokenType.access, user_id, is_admin, config.access_token_lifetime)
        refresh_token = self._get_token_str(TokenType.refresh, user_id, is_admin, config.refresh_token_lifetime)
        return access_token, refresh_token

    def _get_token(self, payload: dict) -> UserToken:
        return UserToken(**payload)

    def _is_valid_token(self, token: UserToken) -> bool:
        return token.user_id != None

    def _get_token_str(self, type: TokenType, user_id: UUID, is_admin: bool, lifetime: timedelta) -> str:
        payload = {
            'type': type.value,
            'user_id': user_id.hex,
            'is_admin': is_admin,
            'exp': time.time() + lifetime.seconds
        }
        return jwt.encode(payload, config.secret_key, algorithm = config.algorithm)
