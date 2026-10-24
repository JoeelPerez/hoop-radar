import os
import tempfile
from pathlib import Path

from common.events.event import Event
from common.file_system_event_layout import FileSystemEventLayout
from ingestion.storage.event_storage import EventStorage


class FileSystemEventStorage(EventStorage):

    def __init__(self, layout: FileSystemEventLayout):
        self.layout = layout

    def store_event(self, event: Event):
        self._write_file(self.layout.build_event_path(event), event)

    def _write_file(self, destination: Path, event: Event):
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=destination.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                tmp.write(event.get_event())
            os.link(tmp_name, destination)
        finally:
            os.unlink(tmp_name)
