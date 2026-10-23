from abc import ABC, abstractmethod

from common.events.event import Event


class EventDownloader(ABC):

    @abstractmethod
    def download_stats_of_match(self, season, team_id, game_code) -> Event:
        pass

    @abstractmethod
    def download_team_players(self, team_id, season) -> Event:
        pass

    @abstractmethod
    def download_player_information(self, player_id) -> Event:
        pass

    @abstractmethod
    def download_team_information(self, team_id) -> Event:
        pass

    @abstractmethod
    def download_league_information(self) -> Event:
        pass

    @abstractmethod
    def download_season_information(self, season) -> Event:
        pass