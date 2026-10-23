from common.events.event import Event, EventMetadata


class EuroleagueEvent(Event):

    def __init__(self, event_string, metadata: EventMetadata):
        super().__init__(event_string, metadata)
