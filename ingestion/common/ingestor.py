from abc import ABC, abstractmethod

from common.event import Event


class Ingestor(ABC):

    @abstractmethod
    def get_stats_of_match(self, team_id, match_id) -> Event:
        pass

    @abstractmethod
    def get_teams_player(self, team_id, season) -> Event:
        pass

    @abstractmethod
    def get_player_information(self, player_id) -> Event:
        pass

    @abstractmethod
    def get_team_information(self, team_id) -> Event:
        pass

    @abstractmethod
    def get_league_information(self) -> Event:
        pass

    @abstractmethod
    def get_season_information(self, season) -> Event:
        pass