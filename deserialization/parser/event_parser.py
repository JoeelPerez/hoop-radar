from abc import ABC, abstractmethod

from common.events.event import Event
from model.league import League
from model.player import Player
from model.season import Season
from model.stat_line import StatLine
from model.team import Team


class EventParser(ABC):

    @abstractmethod
    def parse_stats_of_match_event(self, stats_of_match_event: Event) -> list[StatLine]:
        pass

    @abstractmethod
    def parse_team_players_event(self, team_players_event: Event) -> list[Player]:
        pass

    @abstractmethod
    def parse_player_information_event(self, player_information_event: Event) -> Player:
        pass

    @abstractmethod
    def parse_team_information_event(self, team_information_event: Event) -> Team:
        pass

    @abstractmethod
    def parse_league_information_event(self, league_information_event: Event) -> League:
        pass

    @abstractmethod
    def parse_season_matches_event(self, season_matches_event: Event) -> League:
        pass

    @abstractmethod
    def parse_season_information_event(self, season_information_event: Event) -> Season:
        pass