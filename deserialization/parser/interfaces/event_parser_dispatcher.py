from abc import ABC, abstractmethod

from common.events.event import Event
from deserialization.parser.interfaces.event_parser import EventParser
from deserialization.parser.error.league_mismatch import LeagueMismatch
from deserialization.parser.error.parser_not_found import ParserNotFound


class EventParserDispatcher(ABC):

    def __init__(self):
        self.event_dict = self._index_by_event_type(self._build_event_parsers())

    @property
    @abstractmethod
    def league(self) -> str:
        pass

    @abstractmethod
    def _build_event_parsers(self) -> list[EventParser]:
        pass

    def parse_event(self, event: Event):
        self._ensure_event_is_from_this_league(event)
        return self._find_parser(event).parse_event(event)

    def _index_by_event_type(self, parsers: list[EventParser]) -> dict[str, EventParser]:
        return {parser.event_type: parser for parser in parsers}

    def _ensure_event_is_from_this_league(self, event: Event):
        if event.get_league_event() != self.league:
            raise LeagueMismatch(self.league, event)

    def _find_parser(self, event: Event) -> EventParser:
        parser = self.event_dict.get(event.get_event_type())
        if parser is None:
            raise ParserNotFound(self.league, event.get_event_type())
        return parser
