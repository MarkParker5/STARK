from typing import Any
from enum import Enum
from pydantic import BaseModel


# MARK: - Bridge

class HttpMethod(str, Enum):
    get = 'get'
    post = 'post'
    patch = 'patch'
    delete = 'delete'

BridgeRequestBody = dict[str, Any] | BaseModel

class RestRequest(BaseModel):
    path: str
    method: HttpMethod
    body: BridgeRequestBody

# MARK: - Merlin

class MerlinData(BaseModel):
    device_id: str
    parameter_id: str
    value: str

# MARK: - Socket

class SocketType(str, Enum):
    merlin = 'merlin'
    rest = 'rest'

class SocketData(BaseModel):
    type: SocketType
    data: dict[str, Any]
