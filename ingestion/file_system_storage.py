from common.event import Event
from ingestion.storage import Storage


class FileSystemStorage(Storage):

    def store_stats_of_match(self, event: Event, team_id, match_id, season):
        pass

    def store_players_of_team(self, event: Event, team_id, season):
        pass

    def store_player_information(self, event: Event, player_id):
        pass

    def store_team_information(self, event: Event, team_id):
        pass

    def store_league_information(self, event: Event):
        pass

    def store_season_information(self, event: Event, season):
        pass