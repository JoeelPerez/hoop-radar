class ParserNotFound(Exception):

    def __init__(self, league: str, event_type: str):
        super().__init__(f"No parser registered for events of type {event_type!r} of {league!r}.")
        self.league = league
        self.event_type = event_type
