from abc import ABC, abstractmethod

from common.events.event import Event


class EventParser(ABC):

    @property
    @abstractmethod
    def event_type(self) -> str:
        pass

    @abstractmethod
    def parse_event(self, event: Event):
        pass