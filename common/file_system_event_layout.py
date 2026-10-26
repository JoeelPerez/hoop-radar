import re
from pathlib import Path
from typing import NamedTuple

from common.events.event import Event


class _ParsedFileName(NamedTuple):
    file_base: str
    timestamp: int


class FileSystemEventLayout:

    PARAMETERS_ORDER = ("season", "team_id", "player_id", "game_code")

    _INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    _RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL",
                       *(f"COM{i}" for i in range(1, 10)),
                       *(f"LPT{i}" for i in range(1, 10))}

    _TIMESTAMP_SEPARATOR = "_"

    def __init__(self, root):
        self.root = Path(root).resolve()

    def build_event_path(self, event: Event):
        param_segments = self._build_param_segments(event.get_event_params())
        return (self._build_folders(param_segments, event.get_league_event(), event.get_event_type()) /
                self._build_file_name(param_segments, event.get_league_event(), event.get_event_date()))

    def find_event_files(self, league, event_type, event_params):
        param_segments = self._build_param_segments(event_params)
        directory = self._build_folders(param_segments, league, event_type)
        if not directory.is_dir():
            return []

        file_base = self._build_file_base(league, param_segments)
        return [path for path in directory.iterdir() if path.is_file() and self._is_download_of(path.name, file_base)]

    def sort_event_files(self, files: list[Path]):
        return sorted(files, key=lambda file: self._get_timestamp(file.name))

    def _build_file_name(self, param_segments, league, event_date):
        file_base = self._build_file_base(league, param_segments)
        return f"{file_base}{self._TIMESTAMP_SEPARATOR}{int(event_date * 1000)}{Event.FILE_EXTENSION}"

    def _parse_file_name(self, file_name: str):
        if not file_name.endswith(Event.FILE_EXTENSION):
            return None
        name_without_extension = file_name[:len(file_name) - len(Event.FILE_EXTENSION)]
        file_base, separator, timestamp = name_without_extension.rpartition(self._TIMESTAMP_SEPARATOR)
        if not (separator and file_base and self._is_ascii_number(timestamp)):
            return None
        return _ParsedFileName(file_base, int(timestamp))

    def _is_download_of(self, file_name: str, file_base: str):
        parsed = self._parse_file_name(file_name)
        return parsed is not None and parsed.file_base == file_base

    def _get_timestamp(self, file_name: str):
        parsed = self._parse_file_name(file_name)
        if parsed is None:
            raise ValueError(f"Not an event file name: {file_name!r}")
        return parsed.timestamp

    def _is_ascii_number(self, text: str):
        return text.isascii() and text.isdigit()

    def _build_file_base(self, league, param_segments):
        return param_segments[-1] if param_segments else league

    def _build_folders(self, param_segments, league, event_type):
        for segment in (league, event_type):
            self._validate_segment(segment)
        return self.root.joinpath(league, event_type, *param_segments[:-1])

    def _build_param_segments(self, event_params):
        self._validate_params(event_params)
        param_segments = [f"{event_params[name]}" for name in self.PARAMETERS_ORDER if name in event_params]
        for segment in param_segments:
            self._validate_segment(segment)
        return param_segments

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
