import re
from pathlib import Path

from common.events.event import Event


class FileSystemEventLayout:

    PARAMETERS_ORDER = ("season", "team_id", "player_id", "game_code")

    _INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    _RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL",
                       *(f"COM{i}" for i in range(1, 10)),
                       *(f"LPT{i}" for i in range(1, 10))}

    def __init__(self, root):
        self.root = Path(root).resolve()

    def build_event_path(self, event: Event):
        param_segment = self._build_param_segments(event.get_event_params())
        return (self._build_folders(param_segment, event.get_league_event(), event.get_event_type()) /
                self._build_file_name(param_segment, event.get_league_event(), event.get_event_date()))

    def _build_file_name(self, param_segments, league, event_date):
        file_base = param_segments[-1] if param_segments else league
        return f"{file_base}_{int(event_date * 1000)}{Event.FILE_EXTENSION}"

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
