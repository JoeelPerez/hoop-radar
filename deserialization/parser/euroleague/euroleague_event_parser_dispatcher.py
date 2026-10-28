from common.config import EUROLEAGUE_SOURCE_IDENTIFIER
from deserialization.parser.euroleague.euroleague_season_match_paser import EuroleagueSeasonMatchParser
from deserialization.parser.interfaces.event_parser import EventParser
from deserialization.parser.interfaces.event_parser_dispatcher import EventParserDispatcher


class EuroleagueEventParserDispatcher(EventParserDispatcher):

    league = EUROLEAGUE_SOURCE_IDENTIFIER

    def _build_event_parsers(self) -> list[EventParser]:
        return [
            EuroleagueSeasonMatchParser(),
        ]
