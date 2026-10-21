from abc import ABC, abstractmethod

from common.event import Event


class Storage(ABC):

    def __init__(self, league):
        self.league = league

    @abstractmethod
    def store_stats_of_match(self, event: Event, team_id, match_id, season):
        pass

    @abstractmethod
    def store_players_of_team(self, event: Event, team_id, season):
        pass

    @abstractmethod
    def store_player_information(self, event: Event, player_id):
        pass

    @abstractmethod
    def store_team_information(self, event: Event, team_id):
        pass

    @abstractmethod
    def store_league_information(self, event: Event):
        pass

    @abstractmethod
    def store_season_information(self, event: Event, season):
        pass