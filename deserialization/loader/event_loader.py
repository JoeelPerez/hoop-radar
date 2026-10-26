from abc import ABC, abstractmethod

from common.events.event import Event


class EventLoader(ABC):

    @abstractmethod
    def load_latest_event(self, league, event_type, event_params) -> Event:
        pass

    @abstractmethod
    def load_all_events(self, league, event_type, event_params) -> list[Event]:
        pass

    @abstractmethod
    def load_latest_event_before(self, league, event_type, event_params, event_date: float) -> Event:
        pass
