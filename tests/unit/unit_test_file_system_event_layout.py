import tempfile
import unittest
from pathlib import Path

from common.config import (
    LEAGUE_INFORMATION_EVENT_NAME,
    TEAM_INFORMATION_EVENT_NAME,
    TEAM_PLAYERS_EVENT_NAME,
)
from common.events.event import Event, EventMetadata
from common.file_system_event_layout import FileSystemEventLayout

LEAGUE = "euroleague"
DATE = 1700000000.5


class TestFileSystemEventLayout(unittest.TestCase):

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.root = Path(tmp_dir.name).resolve()
        self.layout = FileSystemEventLayout(self.root)

    def build_event(self, event_type, event_params, event_date=DATE):
        metadata = EventMetadata(
            source_league=LEAGUE,
            event_type=event_type,
            data_format="json",
            event_params=event_params)
        return Event("raw response body", metadata, event_date=event_date)

    def test_build_event_path_uses_all_but_last_parameter_as_folders(self):
        event = self.build_event(TEAM_PLAYERS_EVENT_NAME, {"season": 2024, "team_id": "MAD"})

        path = self.layout.build_event_path(event)

        self.assertEqual(
            self.root / LEAGUE / TEAM_PLAYERS_EVENT_NAME / "2024" / "MAD_1700000000500.json", path)

    def test_build_event_path_without_parameters_is_named_after_league(self):
        event = self.build_event(LEAGUE_INFORMATION_EVENT_NAME, {})

        path = self.layout.build_event_path(event)

        self.assertEqual(
            self.root / LEAGUE / LEAGUE_INFORMATION_EVENT_NAME / "euroleague_1700000000500.json", path)

    def test_build_event_path_follows_defined_order_not_given_order(self):
        in_order = self.build_event(TEAM_PLAYERS_EVENT_NAME, {"season": 2024, "team_id": "MAD"})
        reversed_order = self.build_event(TEAM_PLAYERS_EVENT_NAME, {"team_id": "MAD", "season": 2024})

        self.assertEqual(self.layout.build_event_path(in_order),
                         self.layout.build_event_path(reversed_order))

    def test_build_event_path_rejects_unknown_parameter(self):
        event = self.build_event(TEAM_INFORMATION_EVENT_NAME, {"team_id": "MAD", "phase": "RS"})

        with self.assertRaisesRegex(ValueError, "Parameters without a defined position"):
            self.layout.build_event_path(event)

    def test_build_event_path_rejects_invalid_segments(self):
        invalid_values = ["a:b", "../x", "a/b", "a\\b", "CON", "team ", ""]

        for value in invalid_values:
            with self.subTest(team_id=value):
                event = self.build_event(TEAM_INFORMATION_EVENT_NAME, {"team_id": value})

                with self.assertRaisesRegex(ValueError, "Invalid segment"):
                    self.layout.build_event_path(event)

    def test_build_event_path_rejects_invalid_event_type(self):
        event = self.build_event("../x", {"team_id": "MAD"})

        with self.assertRaisesRegex(ValueError, "Invalid segment"):
            self.layout.build_event_path(event)


if __name__ == "__main__":
    unittest.main()
