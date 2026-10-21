import json
import time
from abc import ABC


class Event(ABC):

    def __init__(self, event_string):
        self.event_string = event_string
        self.event_date = time.time()

    def get_event(self):
        return json.dumps(
            self.__cast_event_to_dict())

    def __cast_event_to_dict(self):
        return {"event": self.event_string, "date": self.event_date}