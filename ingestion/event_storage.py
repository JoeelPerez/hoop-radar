from abc import ABC, abstractmethod

from common.event import Event
from common.config import *

class EventStorage(ABC):

    def __init__(self):
        self.orchestrator_event_type_dict = {
            MATCH_STATS_EVENT_NAME: self.store_stats_of_match,
            TEAM_PLAYERS_EVENT_NAME: self.store_players_of_team,
            PLAYERS_INFORMATION_EVENT_NAME: self.store_player_information,
            TEAM_INFORMATION_EVENT_NAME: self.store_team_information,
            LEAGUE_INFORMATION_EVENT_NAME: self.store_league_information,
            SEASON_INFORMATION_EVENT_NAME: self.store_season_information
        }

    @abstractmethod
    def store_stats_of_match(self, event: Event):
        pass

    @abstractmethod
    def store_players_of_team(self, event: Event):
        pass

    @abstractmethod
    def store_player_information(self, event: Event):
        pass

    @abstractmethod
    def store_team_information(self, event: Event):
        pass

    @abstractmethod
    def store_league_information(self, event: Event):
        pass

    @abstractmethod
    def store_season_information(self, event: Event):
        pass

    def store_event(self, event: Event):
        self.orchestrator_event_type_dict[event.get_event_type()](event)