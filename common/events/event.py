import json
import time
from dataclasses import dataclass, asdict, field


@dataclass(frozen=True)
class EventMetadata:
    source_league: str
    event_type: str
    data_format: str
    event_params: dict = field(default_factory=dict)


class Event:

    FILE_EXTENSION = ".json"

    def __init__(self, event_string, metadata: EventMetadata, event_date=None):
        self.event_string = event_string
        self.metadata = metadata
        self.event_date = time.time() if event_date is None else event_date

    def get_event(self):
        return json.dumps(
            self.__cast_event_to_dict())

    def __cast_event_to_dict(self):
        return {"metadata": asdict(self.metadata),
                "event": self.event_string,
                "date": self.event_date}

    def get_league_event(self):
        return self.metadata.source_league

    def get_event_params(self):
        return self.metadata.event_params

    def get_event_type(self):
        return self.metadata.event_type

    def get_event_date(self):
        return self.event_date
