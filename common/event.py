import json
import time
from abc import ABC
from dataclasses import dataclass, asdict, field


@dataclass(frozen=True)
class EventMetadata:
    source_league: str
    event_type: str
    file_format: str
    event_params: dict = field(default_factory=dict)


class Event(ABC):

    def __init__(self, event_string, metadata: EventMetadata):
        self.event_string = event_string
        self.metadata = metadata
        self.event_date = time.time()

    def get_event(self):
        return json.dumps(
            self.__cast_event_to_dict())

    def __cast_event_to_dict(self):
        return {"metadata": asdict(self.metadata),
                "event": self.event_string,
                "date": self.event_date}
