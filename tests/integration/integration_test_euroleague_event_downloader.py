import json
import os
import unittest
import xml.etree.ElementTree as ElementTree

from ingestion.downloader.euroleague_event_downloader import EuroleagueEventDownloader

CLOSED_SEASON = 2023


@unittest.skipUnless(os.environ.get("RUN_INTEGRATION") == "1",
                     "Integration tests call the real API; set RUN_INTEGRATION=1 to run them")
class TestEuroleagueEventDownloaderIntegration(unittest.TestCase):

    def setUp(self):
        self.downloader = EuroleagueEventDownloader()

    def test_download_stats_of_match(self):
        event = self.downloader.download_stats_of_match(
            season=CLOSED_SEASON, team_id="MAD", game_code=1)

        data = json.loads(event.event_string)
        self.assertTrue(data)

    def test_download_team_players(self):
        event = self.downloader.download_team_players(team_id="MAD", season=2024)

        entries = json.loads(event.event_string)
        players = [entry for entry in entries if entry["type"] == "J"]
        self.assertTrue(players)
        for player in players:
            self.assertEqual("MAD", player["club"]["code"])
            self.assertEqual("E2024", player["season"]["code"])
            self.assertIn("birthDate", player["person"])

    def test_download_player_information(self):
        event = self.downloader.download_player_information(player_id="012656")

        person = json.loads(event.event_string)
        self.assertEqual("012656", person["code"])
        self.assertIn("birthDate", person)

    def test_download_team_information(self):
        event = self.downloader.download_team_information(team_id="MAD")

        club = json.loads(event.event_string)
        self.assertEqual("MAD", club["code"])
        self.assertIn("name", club)

    def test_download_league_information(self):
        event = self.downloader.download_league_information()

        league = json.loads(event.event_string)
        self.assertEqual("E", league["code"])

    def test_download_season_matches(self):
        event = self.downloader.download_season_matches(season=CLOSED_SEASON)

        root = ElementTree.fromstring(event.event_string)
        self.assertEqual("results", root.tag)
        self.assertTrue(root.findall("game"))


if __name__ == "__main__":
    unittest.main()
