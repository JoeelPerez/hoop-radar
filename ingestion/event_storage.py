from abc import ABC, abstractmethod

from common.event import Event


class EventStorage(ABC):

    FILE_EXTENSION = Event.FILE_EXTENSION

    @abstractmethod
    def store_event(self, event: Event):
        pass