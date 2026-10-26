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

    def touch(self, relative_path):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return path

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

    def test_build_event_path_rejects_invalid_folder_segment(self):
        event = self.build_event(TEAM_PLAYERS_EVENT_NAME, {"season": "a:b", "team_id": "MAD"})

        with self.assertRaisesRegex(ValueError, "Invalid segment"):
            self.layout.build_event_path(event)

    def test_build_event_path_rejects_invalid_event_type(self):
        event = self.build_event("../x", {"team_id": "MAD"})

        with self.assertRaisesRegex(ValueError, "Invalid segment"):
            self.layout.build_event_path(event)

    def test_find_event_files_returns_every_download_of_the_entity(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        first = self.touch(folder / "MAD_1700000001000.json")
        second = self.touch(folder / "MAD_1700000002000.json")
        third = self.touch(folder / "MAD_1700000003000.json")

        found = self.layout.find_event_files(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": "MAD"})

        self.assertCountEqual([first, second, third], found)

    def test_find_event_files_ignores_other_entities_and_temporary_files(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        wanted = self.touch(folder / "MAD_1700000001000.json")
        self.touch(folder / "BAR_1700000001000.json")
        self.touch(folder / "MAD_2_1700000001000.json")
        self.touch(folder / "MAD_1700000001000.json.tmp")
        self.touch(folder / "MAD_1700000001000.txt")

        found = self.layout.find_event_files(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": "MAD"})

        self.assertEqual([wanted], found)

    def test_find_event_files_ignores_directories_named_like_event_files(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        wanted = self.touch(folder / "MAD_1700000001000.json")
        (self.root / folder / "MAD_1700000002000.json").mkdir()

        found = self.layout.find_event_files(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": "MAD"})

        self.assertEqual([wanted], found)

    def test_sort_event_files_returns_oldest_first(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        newest = self.touch(folder / "MAD_1700000003000.json")
        oldest = self.touch(folder / "MAD_1700000001000.json")
        middle = self.touch(folder / "MAD_1700000002000.json")

        sorted_files = self.layout.sort_event_files([newest, oldest, middle])

        self.assertEqual([oldest, middle, newest], sorted_files)

    def test_sort_event_files_orders_by_timestamp_value_not_by_text(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        longer = self.touch(folder / "MAD_1000.json")
        shorter = self.touch(folder / "MAD_999.json")

        sorted_files = self.layout.sort_event_files([longer, shorter])

        self.assertEqual([shorter, longer], sorted_files)

    def test_sort_event_files_handles_file_bases_containing_the_separator(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        later = self.touch(folder / "REAL_MADRID_1700000002000.json")
        earlier = self.touch(folder / "REAL_MADRID_1700000001000.json")

        sorted_files = self.layout.sort_event_files([later, earlier])

        self.assertEqual([earlier, later], sorted_files)

    def test_sort_event_files_rejects_files_that_are_not_event_files(self):
        with self.assertRaisesRegex(ValueError, "Not an event file name"):
            self.layout.sort_event_files([Path("notes.txt")])

    def test_find_event_files_looks_inside_parameter_folders(self):
        folder = Path(LEAGUE, TEAM_PLAYERS_EVENT_NAME)
        wanted = self.touch(folder / "2024" / "MAD_1700000001000.json")
        self.touch(folder / "2023" / "MAD_1700000001000.json")

        found = self.layout.find_event_files(
            LEAGUE, TEAM_PLAYERS_EVENT_NAME, {"season": 2024, "team_id": "MAD"})

        self.assertEqual([wanted], found)

    def test_find_event_files_ignores_non_ascii_digits_in_the_timestamp(self):
        folder = Path(LEAGUE, TEAM_INFORMATION_EVENT_NAME)
        wanted = self.touch(folder / "MAD_1700000001000.json")
        self.touch(folder / "MAD_１７０００００００１０００.json")  # fullwidth digits

        found = self.layout.find_event_files(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": "MAD"})

        self.assertEqual([wanted], found)

    def test_find_event_files_returns_empty_when_nothing_is_stored(self):
        found = self.layout.find_event_files(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": "MAD"})
        self.assertEqual([], found)

    def test_find_event_files_rejects_unknown_parameter(self):
        with self.assertRaisesRegex(ValueError, "Parameters without a defined position"):
            self.layout.find_event_files(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"phase": "RS"})

    def test_find_event_files_finds_the_path_built_for_an_event(self):
        event = self.build_event(TEAM_PLAYERS_EVENT_NAME, {"season": 2024, "team_id": "MAD"})
        path = self.touch(self.layout.build_event_path(event).relative_to(self.root))

        found = self.layout.find_event_files(
            event.get_league_event(), event.get_event_type(), event.get_event_params())

        self.assertEqual([path], found)


if __name__ == "__main__":
    unittest.main()
