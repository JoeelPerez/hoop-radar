from abc import ABC, abstractmethod

from common.events.event import Event


class EventParser(ABC):

    @abstractmethod
    def parse_stats_of_match_event(self, stats_of_match_event: Event):
        pass

    @abstractmethod
    def parse_team_player_event(self, team_player_event: Event):
        pass

    @abstractmethod
    def parse_player_information_event(self, player_information_event: Event):
        pass

    @abstractmethod
    def parse_team_information_event(self, team_information_event: Event):
        pass

    @abstractmethod
    def parse_league_information_event(self, league_information_event: Event):
        pass

    @abstractmethod
    def parse_season_information_event(self, season_information_event: Event):
        pass