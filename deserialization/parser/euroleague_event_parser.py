from common.events.event import Event
from deserialization.parser.event_parser import EventParser


class EuroleagueEventParser(EventParser):

    def parse_stats_of_match_event(self, stats_of_match_event: Event):
        pass

    def parse_team_player_event(self, team_player_event: Event):
        pass

    def parse_player_information_event(self, player_information_event: Event):
        pass

    def parse_team_information_event(self, team_information_event: Event):
        pass

    def parse_league_information_event(self, league_information_event: Event):
        pass

    def parse_season_information_event(self, season_information_event: Event):
        pass

