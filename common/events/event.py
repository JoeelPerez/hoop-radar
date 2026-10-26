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

    @classmethod
    def from_json(cls, text):
        event_dict = cls.__parse_json_object(text)
        cls.__require_keys(event_dict, ("metadata", "event", "date"), "event")
        metadata = cls.__parse_metadata(event_dict["metadata"])
        return cls(event_dict["event"], metadata, event_dict["date"])

    @staticmethod
    def __parse_json_object(text):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid event: not valid JSON ({error}).") from error
        if not isinstance(parsed, dict):
            raise ValueError("Invalid event: expected a JSON object.")
        return parsed

    @staticmethod
    def __require_keys(values, keys, description):
        missing = [key for key in keys if key not in values]
        if missing: raise ValueError(f"Incomplete {description}: missing {missing}.")

    @classmethod
    def __parse_metadata(cls, metadata):
        if not isinstance(metadata, dict): raise ValueError("Invalid event: metadata must be a JSON object.")
        cls.__require_keys(metadata, ("source_league", "event_type", "data_format"), "event metadata")
        return EventMetadata(**metadata)

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
