import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from common.events.event import Event
from common.file_system_event_layout import FileSystemEventLayout
from deserialization.loader.file_system_event_loader import FileSystemEventLoader
from ingestion.downloader.euroleague_event_downloader import EuroleagueEventDownloader
from ingestion.storage.file_system_event_storage import FileSystemEventStorage

GET_REQUESTS = "ingestion.downloader.euroleague_event_downloader.get_requests"
PAYLOAD = '{"name": "Dar\u00edo", "values":   [1,2]}'


class TestStorageLoaderRoundTrip(unittest.TestCase):

    def setUp(self):
        patcher = patch(GET_REQUESTS, return_value=Mock(text=PAYLOAD))
        patcher.start()
        self.addCleanup(patcher.stop)
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.layout = FileSystemEventLayout(Path(tmp_dir.name).resolve())
        self.storage = FileSystemEventStorage(self.layout)
        self.loader = FileSystemEventLoader(self.layout)
        downloader = EuroleagueEventDownloader()
        self.downloads = {
            "match_stats": lambda: downloader.download_stats_of_match(season=2024, team_id="MAD", game_code=5),
            "team_players": lambda: downloader.download_team_players(team_id="MAD", season=2024),
            "player_info": lambda: downloader.download_player_information("012656"),
            "team_info": lambda: downloader.download_team_information("MAD"),
            "league_info": lambda: downloader.download_league_information(),
            "season_matches": lambda: downloader.download_season_matches(2024),
        }

    def load_latest(self, event: Event):
        return self.loader.load_latest_event(
            event.get_league_event(), event.get_event_type(), event.get_event_params())

    def test_every_event_type_is_loaded_with_the_parameters_it_was_stored_with(self):
        for name, download in self.downloads.items():
            with self.subTest(event_type=name):
                event = download()
                self.storage.store_event(event)

                loaded = self.load_latest(event)

                self.assertEqual(event.metadata, loaded.metadata)
                self.assertEqual(PAYLOAD, loaded.event_string)
                self.assertEqual(event.get_event_date(), loaded.get_event_date())

    def test_every_event_type_is_found_at_the_path_it_was_stored(self):
        for name, download in self.downloads.items():
            with self.subTest(event_type=name):
                event = download()
                self.storage.store_event(event)

                found = self.layout.find_event_files(
                    event.get_league_event(), event.get_event_type(), event.get_event_params())

                self.assertEqual([self.layout.build_event_path(event)], found)

    def test_every_event_type_is_loaded_by_its_own_date(self):
        for name, download in self.downloads.items():
            with self.subTest(event_type=name):
                event = download()
                self.storage.store_event(event)

                loaded = self.loader.load_latest_event_before(
                    event.get_league_event(), event.get_event_type(), event.get_event_params(),
                    event.get_event_date())

                self.assertEqual(event.get_event_date(), loaded.get_event_date())

    def test_every_event_type_keeps_all_its_downloads(self):
        for name, download in self.downloads.items():
            with self.subTest(event_type=name):
                first = download()
                second = Event(PAYLOAD, first.metadata, event_date=first.get_event_date() + 1)
                self.storage.store_event(first)
                self.storage.store_event(second)

                loaded = self.loader.load_all_events(
                    first.get_league_event(), first.get_event_type(), first.get_event_params())

                self.assertEqual([first.get_event_date(), second.get_event_date()],
                                 [event.get_event_date() for event in loaded])

    def test_parameters_are_matched_by_their_text_value(self):
        event = self.downloads["match_stats"]()
        self.storage.store_event(event)

        loaded = self.loader.load_latest_event(
            "euroleague", "match_stats", {"season": "2024", "game_code": "5"})

        self.assertEqual(event.get_event_date(), loaded.get_event_date())


if __name__ == "__main__":
    unittest.main()
