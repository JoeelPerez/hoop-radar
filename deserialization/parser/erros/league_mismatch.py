from common.events.event import Event


class LeagueMismatch(Exception):

    def __init__(self, expected_league: str, event: Event):
        super().__init__(f"This dispatcher parses events of {expected_league!r}, but received an event of "
                         f"{event.get_league_event()!r} (type {event.get_event_type()!r}).")
        self.expected_league = expected_league
        self.event = event
