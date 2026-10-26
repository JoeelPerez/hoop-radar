from pathlib import Path

from common.events.event import Event
from common.events.event_not_found import EventNotFound
from common.file_system_event_layout import FileSystemEventLayout
from deserialization.loader.event_loader import EventLoader


class FileSystemEventLoader(EventLoader):

    def __init__(self, layout: FileSystemEventLayout):
        self.layout = layout

    def load_latest_event(self, league, event_type, event_params):
        files = self._find_sorted_files(league, event_type, event_params)
        return self._read_event(self._pick_latest(files, league, event_type, event_params))

    def load_all_events(self, league, event_type, event_params):
        files = self._find_sorted_files(league, event_type, event_params)
        return [self._read_event(file) for file in files]

    def load_latest_event_before(self, league, event_type, event_params, event_date: float):
        limit = self.layout.to_timestamp(event_date)
        files = self._find_sorted_files(league, event_type, event_params)
        files_up_to_limit = [file for file in files if self.layout.get_file_timestamp(file) <= limit]
        return self._read_event(self._pick_latest(files_up_to_limit, league, event_type, event_params))

    def _find_sorted_files(self, league, event_type, event_params):
        return self.layout.sort_event_files(self.layout.find_event_files(league, event_type, event_params))

    def _pick_latest(self, sorted_files: list[Path], league, event_type, event_params):
        if not sorted_files:
            raise EventNotFound(league, event_type, event_params)
        return sorted_files[-1]

    def _read_event(self, file: Path):
        try:
            return Event.from_json(file.read_text(encoding="utf-8"))
        except ValueError as error:
            raise ValueError(f"Cannot load event file {file}: {error}") from error
