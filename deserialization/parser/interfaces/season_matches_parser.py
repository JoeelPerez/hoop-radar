from abc import ABC, abstractmethod

from common.config import SEASON_MATCHES_EVENT_NAME
from common.events.event import Event
from deserialization.parser.interfaces.event_parser import EventParser
from model.match import Match


class SeasonMatchesParser(EventParser, ABC):

    event_type = SEASON_MATCHES_EVENT_NAME

    @abstractmethod
    def parse_event(self, event: Event) -> list[Match]:
        pass