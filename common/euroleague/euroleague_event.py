from common.event import Event


class EuroLeagueEvent(Event):

    def __init__(self, event_string):
        super().__init__(event_string)