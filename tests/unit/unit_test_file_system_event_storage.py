import tempfile
import unittest
from pathlib import Path

from common.config import (
    LEAGUE_INFORMATION_EVENT_NAME,
    MATCH_STATS_EVENT_NAME,
    PLAYERS_INFORMATION_EVENT_NAME,
    SEASON_INFORMATION_EVENT_NAME,
    TEAM_INFORMATION_EVENT_NAME,
    TEAM_PLAYERS_EVENT_NAME,
)
from common.euroleague.euroleague_event import EuroleagueEvent
from common.event import EventMetadata
from ingestion.file_system_event_storage import FileSystemEventStorage

LEAGUE = "euroleague"


class TestFileSystemEventStorage(unittest.TestCase):

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.root = Path(tmp_dir.name).resolve()
        self.storage = FileSystemEventStorage(self.root)

    def build_event(self, event_type, data_format, event_params):
        metadata = EventMetadata(
            source_league=LEAGUE,
            event_type=event_type,
            data_format=data_format,
            event_params=event_params)
        return EuroleagueEvent("raw response body", metadata)

    def timestamp(self, event):
        return int(event.get_event_date() * 1000)

    def assert_stored_at(self, event, expected_relative_path):
        stored_files = [path for path in self.root.rglob("*") if path.is_file()]
        self.assertEqual([self.root / expected_relative_path], stored_files)
        self.assertEqual(event.get_event(), stored_files[0].read_text(encoding="utf-8"))

    def test_store_match_stats_event(self):
        event = self.build_event(MATCH_STATS_EVENT_NAME, "json",
                                 {"season": 2024, "game_code": 5})

        self.storage.store_event(event)
        self.assert_stored_at(event, Path(LEAGUE, MATCH_STATS_EVENT_NAME, "2024",
                                          f"5_{self.timestamp(event)}.json"))

    def test_store_team_players_event(self):
        event = self.build_event(TEAM_PLAYERS_EVENT_NAME, "json",
                                 {"season": 2024, "team_id": "MAD"})

        self.storage.store_event(event)
        self.assert_stored_at(event, Path(LEAGUE, TEAM_PLAYERS_EVENT_NAME, "2024",
                                          f"MAD_{self.timestamp(event)}.json"))

    def test_store_player_information_event(self):
        event = self.build_event(PLAYERS_INFORMATION_EVENT_NAME, "json",
                                 {"player_id": "012656"})

        self.storage.store_event(event)
        self.assert_stored_at(event, Path(LEAGUE, PLAYERS_INFORMATION_EVENT_NAME,
                                          f"012656_{self.timestamp(event)}.json"))

    def test_store_team_information_event(self):
        event = self.build_event(TEAM_INFORMATION_EVENT_NAME, "json",
                                 {"team_id": "MAD"})

        self.storage.store_event(event)
        self.assert_stored_at(event, Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME,
                                          f"MAD_{self.timestamp(event)}.json"))

    def test_store_league_information_event(self):
        event = self.build_event(LEAGUE_INFORMATION_EVENT_NAME, "json", {})

        self.storage.store_event(event)
        self.assert_stored_at(event, Path(LEAGUE, LEAGUE_INFORMATION_EVENT_NAME,
                                          f"{LEAGUE}_{self.timestamp(event)}.json"))

    def test_store_season_information_event(self):
        event = self.build_event(SEASON_INFORMATION_EVENT_NAME, "xml",
                                 {"season": 2024})

        self.storage.store_event(event)
        self.assert_stored_at(event, Path(LEAGUE, SEASON_INFORMATION_EVENT_NAME,
                                          f"2024_{self.timestamp(event)}.json"))


if __name__ == "__main__":
    unittest.main()
