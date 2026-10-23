import unittest
from unittest.mock import Mock, patch

from common.config import (
    LEAGUE_INFORMATION_EVENT_NAME,
    MATCH_STATS_EVENT_NAME,
    PLAYERS_INFORMATION_EVENT_NAME,
    SEASON_INFORMATION_EVENT_NAME,
    TEAM_INFORMATION_EVENT_NAME,
    TEAM_PLAYERS_EVENT_NAME,
)
from common.events.euroleague_event import EuroleagueEvent
from ingestion.downloader.euroleague_event_downloader import EuroleagueEventDownloader


GET_REQUESTS = "ingestion.downloader.euroleague_event_downloader.get_requests"
RESPONSE_TEXT = "raw response body"
API = "https://api-live.euroleague.net"


class TestEuroleagueEventDownloader(unittest.TestCase):

    def setUp(self):
        patcher = patch(GET_REQUESTS, return_value=Mock(text=RESPONSE_TEXT))
        self.get_requests = patcher.start()
        self.addCleanup(patcher.stop)
        self.downloader = EuroleagueEventDownloader()

    def assert_event(self, event, event_type, data_format, event_params):
        self.assertIsInstance(event, EuroleagueEvent)
        self.assertEqual(RESPONSE_TEXT, event.event_string)
        self.assertEqual("euroleague", event.metadata.source_league)
        self.assertEqual(event_type, event.metadata.event_type)
        self.assertEqual(data_format, event.metadata.data_format)
        self.assertEqual(event_params, event.metadata.event_params)

    def test_download_stats_of_match(self):
        event = self.downloader.download_stats_of_match(
            season=2024, team_id="MAD", game_code=5)

        self.get_requests.assert_called_once_with(
            f"{API}/v3/competitions/E/seasons/E2024/games/5/stats")
        self.assert_event(event, MATCH_STATS_EVENT_NAME, "json",
                          {"season": 2024, "game_code": 5})

    def test_download_team_players(self):
        event = self.downloader.download_team_players(
            team_id="MAD", season=2024)

        self.get_requests.assert_called_once_with(
            f"{API}/v2/competitions/E/seasons/E2024/clubs/MAD/people")
        self.assert_event(event, TEAM_PLAYERS_EVENT_NAME, "json",
                          {"season": 2024, "team_id": "MAD"})

    def test_download_player_information(self):
        event = self.downloader.download_player_information(
            player_id="012656")

        self.get_requests.assert_called_once_with(
            f"{API}/v2/people/012656")
        self.assert_event(event, PLAYERS_INFORMATION_EVENT_NAME, "json",
                          {"player_id": "012656"})

    def test_download_team_information(self):
        event = self.downloader.download_team_information(team_id="MAD")

        self.get_requests.assert_called_once_with(
            f"{API}/v2/clubs/MAD")
        self.assert_event(event, TEAM_INFORMATION_EVENT_NAME, "json",
                          {"team_id": "MAD"})

    def test_download_league_information(self):
        event = self.downloader.download_league_information()

        self.get_requests.assert_called_once_with(
            f"{API}/v2/competitions/E")
        self.assert_event(event, LEAGUE_INFORMATION_EVENT_NAME, "json", {})

    def test_download_season_information(self):
        event = self.downloader.download_season_information(season=2024)

        self.get_requests.assert_called_once_with(
            f"{API}/v1/results/", params={"seasonCode": "E2024"})
        self.assert_event(event, SEASON_INFORMATION_EVENT_NAME, "xml",
                          {"season": 2024})


if __name__ == "__main__":
    unittest.main()
