from euroleague_api.EuroLeagueData import EuroLeagueData
from euroleague_api.utils import get_requests

from common.config import *
from common.events.euroleague_event import EuroleagueEvent
from common.events.event import EventMetadata
from ingestion.downloader.event_downloader import EventDownloader


class EuroleagueEventDownloader(EventDownloader):

    SOURCE = "euroleague"

    def __init__(self):
        self.__api = EuroLeagueData("E")

    def download_stats_of_match(self, season, team_id, game_code) -> EuroleagueEvent:
        url = self.__api.make_season_game_url(season, game_code, "stats")
        response = get_requests(url)
        return self.__create_euroleague_event(
            response.text, MATCH_STATS_EVENT_NAME, "json",
            {"season": season, "game_code": game_code})

    def download_team_players(self, team_id, season) -> EuroleagueEvent:
        url = (f"{self.__api.url_v2}/seasons/{self.__api.competition}{season}"
               f"/clubs/{team_id}/people")
        response = get_requests(url)
        return self.__create_euroleague_event(
            response.text, TEAM_PLAYERS_EVENT_NAME, "json",
            {"season": season, "team_id": team_id})

    def download_player_information(self, player_id) -> EuroleagueEvent:
        url = f"{self.__api.BASE_URL}/{self.__api.V2}/people/{player_id}"
        response = get_requests(url)
        return self.__create_euroleague_event(
            response.text, PLAYERS_INFORMATION_EVENT_NAME, "json", {"player_id": player_id})

    def download_team_information(self, team_id) -> EuroleagueEvent:
        url = f"{self.__api.BASE_URL}/{self.__api.V2}/clubs/{team_id}"
        response = get_requests(url)
        return self.__create_euroleague_event(
            response.text, TEAM_INFORMATION_EVENT_NAME, "json", {"team_id": team_id})

    def download_league_information(self) -> EuroleagueEvent:

        # TODO Buscar maneras de cargar información relevante sobre la euroliga

        response = get_requests(self.__api.url_v2)
        return self.__create_euroleague_event(
            response.text, LEAGUE_INFORMATION_EVENT_NAME, "json", {})

    def download_season_information(self, season) -> EuroleagueEvent:
        response = get_requests(
            self.__api.url_v1,
            params={"seasonCode": f"{self.__api.competition}{season}"})
        return self.__create_euroleague_event(
            response.text, SEASON_INFORMATION_EVENT_NAME, "xml", {"season": season})

    def __create_euroleague_event(self, string_event, event_type, data_format,
                                  event_params):
        metadata = EventMetadata(
            source_league=self.SOURCE,
            event_type=event_type,
            data_format=data_format,
            event_params={**event_params})
        return EuroleagueEvent(string_event, metadata)
