import json
import tempfile
import unittest
from pathlib import Path

from common.config import (
    LEAGUE_INFORMATION_EVENT_NAME,
    TEAM_INFORMATION_EVENT_NAME,
    TEAM_PLAYERS_EVENT_NAME,
)
from common.events.event import Event, EventMetadata
from common.events.event_not_found import EventNotFound
from common.file_system_event_layout import FileSystemEventLayout
from deserialization.loader.file_system_event_loader import FileSystemEventLoader
from ingestion.storage.file_system_event_storage import FileSystemEventStorage

LEAGUE = "euroleague"
FIRST = 1700000001.0
SECOND = 1700000002.0
THIRD = 1700000003.0


class TestFileSystemEventLoader(unittest.TestCase):

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.root = Path(tmp_dir.name).resolve()
        layout = FileSystemEventLayout(self.root)
        self.storage = FileSystemEventStorage(layout)
        self.loader = FileSystemEventLoader(layout)

    def store(self, event_date, payload="raw response body", event_type=TEAM_INFORMATION_EVENT_NAME,
              event_params=None):
        metadata = EventMetadata(
            source_league=LEAGUE,
            event_type=event_type,
            data_format="json",
            event_params={"team_id": "MAD"} if event_params is None else event_params)
        event = Event(payload, metadata, event_date=event_date)
        self.storage.store_event(event)
        return event

    def load_latest(self, team_id="MAD"):
        return self.loader.load_latest_event(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": team_id})

    def load_all(self, team_id="MAD"):
        return self.loader.load_all_events(LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": team_id})

    def load_before(self, event_date, team_id="MAD"):
        return self.loader.load_latest_event_before(
            LEAGUE, TEAM_INFORMATION_EVENT_NAME, {"team_id": team_id}, event_date)

    def test_load_latest_event_returns_the_event_that_was_stored(self):
        stored = self.store(FIRST, payload='{"name": "Real Madrid"}')

        loaded = self.load_latest()

        self.assertEqual(stored.metadata, loaded.metadata)
        self.assertEqual(stored.event_string, loaded.event_string)
        self.assertEqual(stored.get_event_date(), loaded.get_event_date())

    def test_load_latest_event_returns_the_most_recent_download(self):
        self.store(SECOND, payload="second")
        self.store(THIRD, payload="third")
        self.store(FIRST, payload="first")

        self.assertEqual("third", self.load_latest().event_string)

    def test_load_latest_event_orders_by_timestamp_value_not_by_text(self):
        self.store(999.0, payload="shorter timestamp")
        self.store(1000.0, payload="longer timestamp")

        self.assertEqual("longer timestamp", self.load_latest().event_string)

    def test_load_latest_event_does_not_mix_entities(self):
        self.store(FIRST, payload="madrid")
        self.store(SECOND, payload="barcelona", event_params={"team_id": "BAR"})

        self.assertEqual("madrid", self.load_latest("MAD").event_string)
        self.assertEqual("barcelona", self.load_latest("BAR").event_string)

    def test_load_latest_event_does_not_mix_seasons(self):
        for season, payload in ((2023, "old season"), (2024, "new season")):
            self.store(FIRST, payload=payload, event_type=TEAM_PLAYERS_EVENT_NAME,
                       event_params={"season": season, "team_id": "MAD"})

        loaded = self.loader.load_latest_event(
            LEAGUE, TEAM_PLAYERS_EVENT_NAME, {"season": 2023, "team_id": "MAD"})

        self.assertEqual("old season", loaded.event_string)

    def test_load_latest_event_works_for_events_without_parameters(self):
        self.store(FIRST, payload="league data", event_type=LEAGUE_INFORMATION_EVENT_NAME, event_params={})

        loaded = self.loader.load_latest_event(LEAGUE, LEAGUE_INFORMATION_EVENT_NAME, {})

        self.assertEqual("league data", loaded.event_string)

    def test_load_latest_event_keeps_non_ascii_text(self):
        self.store(FIRST, payload="Dar\u00edo \u0160ari\u0107")

        self.assertEqual("Dar\u00edo \u0160ari\u0107", self.load_latest().event_string)

    def test_load_latest_event_reads_files_written_as_raw_utf8(self):
        stored = self.store(FIRST, payload="placeholder")
        path = self.loader.layout.build_event_path(stored)
        envelope = {"metadata": {"source_league": LEAGUE, "event_type": TEAM_INFORMATION_EVENT_NAME,
                                 "data_format": "json", "event_params": {"team_id": "MAD"}},
                    "event": "Dar\u00edo \u0160ari\u0107", "date": FIRST}
        path.write_bytes(json.dumps(envelope, ensure_ascii=False).encode("utf-8"))

        self.assertEqual("Dar\u00edo \u0160ari\u0107", self.load_latest().event_string)

    def test_load_latest_event_raises_when_nothing_is_stored(self):
        with self.assertRaisesRegex(EventNotFound, "team_info"):
            self.load_latest()

    def test_load_latest_event_raises_when_only_other_entities_are_stored(self):
        self.store(FIRST, event_params={"team_id": "BAR"})

        with self.assertRaises(EventNotFound):
            self.load_latest("MAD")

    def test_load_latest_event_reports_a_corrupt_file_instead_of_falling_back(self):
        self.store(FIRST, payload="valid")
        corrupt = self.store(SECOND, payload="will be corrupted")
        corrupt_path = self.loader.layout.build_event_path(corrupt)
        corrupt_path.write_text("not json", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Cannot load event file .*not valid JSON"):
            self.load_latest()

    def test_load_all_events_returns_every_download_oldest_first(self):
        self.store(THIRD, payload="third")
        self.store(FIRST, payload="first")
        self.store(SECOND, payload="second")

        self.assertEqual(["first", "second", "third"], [event.event_string for event in self.load_all()])

    def test_load_all_events_only_returns_the_requested_entity(self):
        self.store(FIRST, payload="madrid")
        self.store(SECOND, payload="barcelona", event_params={"team_id": "BAR"})

        self.assertEqual(["madrid"], [event.event_string for event in self.load_all("MAD")])

    def test_load_all_events_returns_empty_list_when_nothing_is_stored(self):
        self.assertEqual([], self.load_all())

    def test_load_latest_event_before_returns_the_latest_download_not_after_the_date(self):
        self.store(FIRST, payload="first")
        self.store(THIRD, payload="third")

        self.assertEqual("first", self.load_before(SECOND).event_string)

    def test_load_latest_event_before_includes_a_download_made_exactly_at_the_date(self):
        self.store(FIRST, payload="first")
        self.store(SECOND, payload="second")

        self.assertEqual("second", self.load_before(SECOND).event_string)

    def test_load_latest_event_before_takes_the_date_in_seconds(self):
        self.store(FIRST, payload="first")
        self.store(SECOND, payload="second")

        self.assertEqual("first", self.load_before(SECOND - 0.5).event_string)
        self.assertEqual("second", self.load_before(SECOND + 0.5).event_string)

    def test_load_latest_event_before_returns_the_latest_when_the_date_is_after_all(self):
        self.store(FIRST, payload="first")
        self.store(SECOND, payload="second")

        self.assertEqual("second", self.load_before(THIRD * 10).event_string)

    def test_load_latest_event_before_raises_when_every_download_is_later(self):
        self.store(SECOND)

        with self.assertRaises(EventNotFound):
            self.load_before(FIRST)

    def test_load_latest_event_before_raises_when_nothing_is_stored(self):
        with self.assertRaises(EventNotFound):
            self.load_before(FIRST)


if __name__ == "__main__":
    unittest.main()
