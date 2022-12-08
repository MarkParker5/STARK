from typing import Any, Optional
from .NotificationName import NotificationName

class Notification:
    name: NotificationName
    object: Any
    data: dict

    def __init__(self, name: NotificationName, object: Optional[Any], data: dict):
        self.name = name
        self.object = object
        self.data = data
