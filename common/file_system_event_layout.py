import re
from pathlib import Path

from common.events.event import Event


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

        prefix = self._build_file_name_prefix(league, param_segments)
        return [path for path in directory.iterdir() if self._is_download_of(path.name, prefix)]

    def sort_event_files(self, files: list[Path]):
        return sorted(files, key=lambda file: self._extract_timestamp(file.name))

    def _build_file_name(self, param_segments, league, event_date):
        return f"{self._build_file_name_prefix(league, param_segments)}{int(event_date * 1000)}{Event.FILE_EXTENSION}"

    def _build_file_name_prefix(self, league, param_segments) -> str:
        return f"{self._build_file_base(league, param_segments)}{self._TIMESTAMP_SEPARATOR}"

    def _is_download_of(self, file_name: str, prefix: str) -> bool:
        if not (file_name.startswith(prefix) and file_name.endswith(Event.FILE_EXTENSION)):
            return False
        return self._has_only_ascii_digits_after_prefix(file_name, prefix)

    def _has_only_ascii_digits_after_prefix(self, file_name: str, prefix: str) -> bool:
        timestamp = file_name[len(prefix):len(file_name) - len(Event.FILE_EXTENSION)]
        return self._is_ascii_number(timestamp)

    def _is_ascii_number(self, text: str) -> bool:
        return text.isascii() and text.isdigit()

    def _extract_timestamp(self, file_name: str) -> int:
        timestamp = file_name[:len(file_name) - len(Event.FILE_EXTENSION)].rsplit(self._TIMESTAMP_SEPARATOR, 1)[-1]
        if not (file_name.endswith(Event.FILE_EXTENSION) and self._is_ascii_number(timestamp)):
            raise ValueError(f"Not an event file name: {file_name!r}")
        return int(timestamp)

    def _build_file_base(self, league, param_segments) -> str:
        return param_segments[-1] if param_segments else league

    def _build_folders(self, param_segments, league, event_type):
        for segment in param_segments + [league, event_type]:
            self._validate_segment(segment)
        return self.root.joinpath(league, event_type, *param_segments[:-1])

    def _build_param_segments(self, event_params):
        self._validate_params(event_params)
        return [f"{event_params[name]}" for name in self.PARAMETERS_ORDER if name in event_params]

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
