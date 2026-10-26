class EventNotFound(Exception):

    def __init__(self, league, event_type, event_params):
        super().__init__(f"No stored event for league={league!r}, event_type={event_type!r}, "
                         f"event_params={event_params!r}.")
        self.league = league
        self.event_type = event_type
        self.event_params = event_params
