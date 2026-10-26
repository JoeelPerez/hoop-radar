from abc import ABC, abstractmethod


class EventLoader(ABC):

    @abstractmethod
    def load_event(self, league, event_type, event_params):
        pass

    @abstractmethod
    def load_all_events(self, league, event_type, event_params):
        pass

    @abstractmethod
    def load_event_by_date(self, league, event_type, event_params, timestamp):
        pass