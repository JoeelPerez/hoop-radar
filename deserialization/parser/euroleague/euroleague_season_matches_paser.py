from common.events.event import Event
from deserialization.parser.interfaces.season_matches_parser import SeasonMatchesParser
from model.match import Match


class EuroleagueSeasonMatchesParser(SeasonMatchesParser):
    def parse_event(self, event: Event) -> list[Match]:
        pass