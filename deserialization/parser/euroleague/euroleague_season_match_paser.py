from common.events.event import Event
from deserialization.parser.interfaces.season_match_parser import SeasonMatchParser
from model.match import Match


class EuroleagueSeasonMatchParser(SeasonMatchParser):
    def parse_event(self, event: Event) -> list[Match]:
        pass