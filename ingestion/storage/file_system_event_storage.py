import os
import re
import tempfile
from pathlib import Path

from common.events.event import Event
from ingestion.storage.event_storage import EventStorage


class FileSystemEventStorage(EventStorage):


    PARAMETERS_ORDER = ("season", "team_id", "player_id", "game_code")

    _INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    _RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL",
                       *(f"COM{i}" for i in range(1, 10)),
                       *(f"LPT{i}" for i in range(1, 10))}

    def __init__(self, root):
        self.root = Path(root).resolve()

    def store_event(self, event: Event):
        self._validate_params(event.get_event_params())
        param_segments = self._build_param_segments(event.get_event_params())
        folders = param_segments[:-1]
        file_name_base = param_segments[-1] if param_segments else event.get_league_event()
        file_name = self._file_name(file_name_base, event.get_event_date())
        destination = self._build_full_path(event, folders, file_name)
        self._write_file(destination, event)

    def _build_param_segments(self, event_params):
        keys = [f"{event_params[name]}" for name in self.PARAMETERS_ORDER if name in event_params]
        for segment in keys:
            self._validate_segment(segment)
        return keys

    def _file_name(self, file_name_base, event_date):
        return f"{file_name_base}_{int(event_date * 1000)}{self.FILE_EXTENSION}"

    def _build_full_path(self, event: Event, param_segments: list[str], filename: str) -> Path:
        return self.root.joinpath(event.get_league_event(), event.get_event_type(), *param_segments, filename)

    def _write_file(self, destination: Path, event: Event):
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=destination.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                tmp.write(event.get_event())
            os.link(tmp_name, destination)
        finally:
            os.unlink(tmp_name)

    def _validate_params(self, event_params):
        unknown = set(event_params) - set(self.PARAMETERS_ORDER)
        if unknown:
            raise ValueError(
                f"Parameters without a defined position: {sorted(unknown)}.")

    def _validate_segment(self, segment: str):
        stem = segment.split(".")[0].upper()
        if (not segment
                or segment in (".", "..")
                or self._INVALID_CHARS.search(segment)
                or segment.endswith((" ", "."))
                or stem in self._RESERVED_NAMES):
            raise ValueError(f"Invalid segment for the file system: "
                             f"{segment!r}")
