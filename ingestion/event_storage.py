from abc import ABC, abstractmethod

from common.event import Event


class EventStorage(ABC):

    @abstractmethod
    def store_event(self, event: Event):
        pass