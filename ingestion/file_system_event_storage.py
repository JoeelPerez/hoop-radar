from common.event import Event
from ingestion.event_storage import EventStorage


class FileSystemEventStorage(EventStorage):

    def store_stats_of_match(self, event: Event):
        pass

    def store_players_of_team(self, event: Event):
        pass

    def store_player_information(self, event: Event):
        pass

    def store_team_information(self, event: Event):
        pass

    def store_league_information(self, event: Event):
        pass

    def store_season_information(self, event: Event):
        pass