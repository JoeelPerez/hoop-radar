import os
import re
import tempfile
from pathlib import Path

from common.event import Event
from ingestion.event_storage import EventStorage


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
        param_segments, filename = self._build_path_parts(event.get_event_params(), event.get_event_date())
        for segment in param_segments:
            self._validate_segment(segment)
        self._write_file(self._build_full_path(event, param_segments, filename), event)

    def _build_full_path(self, event: Event, param_segments: list[str], filename: str) -> Path:
        return self.root.joinpath(event.get_league_event(), event.get_event_type(), *param_segments, filename)

    def _build_path_parts(self, event_params, event_date):
        param_segments = [f"{event_params[name]}" for name in self.PARAMETERS_ORDER if name in event_params]
        return param_segments, f"{int(event_date * 1000)}.json"

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
