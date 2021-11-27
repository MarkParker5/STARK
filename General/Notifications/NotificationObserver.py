from typing import Callable

from .. import Identifable, threadingFunction
from . import Notification, NotificationName

NotificationCallback = Callable[[Notification,], None]

class NotificationObserver(Identifable):
    notificationName: NotificationName
    callback: NotificationCallback

    def __init__(self, notificationName: NotificationName, callback: NotificationCallback):
        super().__init__()
        self.notificationName = notificationName
        self.callback = threadingFunction(callback)
