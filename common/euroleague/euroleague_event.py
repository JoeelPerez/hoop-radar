from common.event import Event


class EuroleagueEvent(Event):

    def __init__(self, event_string):
        super().__init__(event_string)