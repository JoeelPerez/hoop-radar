from common.event import Event
from ingestion.common.event_downloader import EventDownloader


class EuroleagueEventDownloader(EventDownloader):

    def download_stats_of_match(self, team_id, match_id) -> Event:
        pass

    def download_teams_player(self, team_id, season) -> Event:
        pass

    def download_player_information(self, player_id) -> Event:
        pass

    def download_team_information(self, team_id) -> Event:
        pass

    def download_league_information(self) -> Event:
        pass

    def download_season_information(self, season) -> Event:
        pass