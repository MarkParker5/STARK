from typing import Any, Optional

from .. import Singleton, UUID
from . import Notification, NotificationName, NotificationObserver, NotificationCallback

class NotificationCenter(Singleton):
    _observers: dict[NotificationName, list[NotificationObserver]] = {}

    def post(self, name: NotificationName, object: Optional[Any] = None, data: dict = []):
        notify = Notification(name = name, object = object, data = data)
        for obser in self._observers.get(name) or []:
            obser.callback(notify)

    def addObserver(self, notificationName: NotificationName, callback: NotificationCallback) -> NotificationObserver:
        if not notificationName in self._observers.keys() :
            self._observers[notificationName] = []

        observer = NotificationObserver(notificationName, callback)
        self._observers[notificationName].append(observer)

        return observer

    def removeObserver(self, observer: NotificationObserver):
        if observer in self._observers.get(observer.notificationName) or []:
            self._observers.get(observer.notificationName).remove(observer)
