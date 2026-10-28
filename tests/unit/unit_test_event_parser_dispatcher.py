import unittest

from common.config import (
    SEASON_MATCHES_EVENT_NAME,
    TEAM_INFORMATION_EVENT_NAME,
    EUROLEAGUE_SOURCE_IDENTIFIER,
)
from common.events.event import Event, EventMetadata
from deserialization.parser.euroleague.euroleague_event_parser_dispatcher import EuroleagueEventParserDispatcher
from deserialization.parser.interfaces.event_parser import EventParser
from deserialization.parser.interfaces.event_parser_dispatcher import EventParserDispatcher
from deserialization.parser.interfaces.season_matches_parser import SeasonMatchesParser
from deserialization.parser.error.league_mismatch import LeagueMismatch
from deserialization.parser.error.parser_not_found import ParserNotFound


class RecordingParser(EventParser):

    def __init__(self, result):
        self.result = result
        self.received = []

    def parse_event(self, event):
        self.received.append(event)
        return self.result


class SeasonMatchesRecordingParser(RecordingParser):
    event_type = SEASON_MATCHES_EVENT_NAME


class TeamInfoRecordingParser(RecordingParser):
    event_type = TEAM_INFORMATION_EVENT_NAME


class FakeDispatcher(EventParserDispatcher):

    league = "fake_league"

    def __init__(self, season_matches_parser, team_info_parser):
        self.season_matches_parser = season_matches_parser
        self.team_info_parser = team_info_parser
        super().__init__()

    def _build_event_parsers(self):
        return [self.season_matches_parser, self.team_info_parser]


def build_event(event_type, league="fake_league"):
    return Event("payload", EventMetadata(league, event_type, "xml", {"season": 2023}))


class TestEventParserDispatcher(unittest.TestCase):

    def setUp(self):
        self.season_matches_parser = SeasonMatchesRecordingParser("season matches result")
        self.team_info_parser = TeamInfoRecordingParser("team info result")
        self.dispatcher = FakeDispatcher(self.season_matches_parser, self.team_info_parser)

    def test_dispatcher_base_class_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            EventParserDispatcher()

    def test_a_dispatcher_without_a_league_cannot_be_instantiated(self):
        class WithoutLeague(EventParserDispatcher):
            def _build_event_parsers(self):
                return []

        with self.assertRaises(TypeError):
            WithoutLeague()

    def test_a_dispatcher_without_parsers_cannot_be_instantiated(self):
        class WithoutParsers(EventParserDispatcher):
            league = "fake_league"

        with self.assertRaises(TypeError):
            WithoutParsers()

    def test_a_parser_without_event_type_cannot_be_instantiated(self):
        class WithoutEventType(EventParser):
            def parse_event(self, event):
                pass

        with self.assertRaises(TypeError):
            WithoutEventType()

    def test_registers_each_parser_under_its_own_event_type(self):
        self.assertEqual({SEASON_MATCHES_EVENT_NAME: self.season_matches_parser,
                          TEAM_INFORMATION_EVENT_NAME: self.team_info_parser},
                         self.dispatcher.event_dict)

    def test_parses_the_event_with_the_parser_of_its_type_and_returns_its_result(self):
        event = build_event(SEASON_MATCHES_EVENT_NAME)

        result = self.dispatcher.parse_event(event)

        self.assertEqual("season matches result", result)
        self.assertEqual([event], self.season_matches_parser.received)
        self.assertEqual([], self.team_info_parser.received)

    def test_each_event_type_goes_to_its_own_parser(self):
        result = self.dispatcher.parse_event(build_event(TEAM_INFORMATION_EVENT_NAME))

        self.assertEqual("team info result", result)
        self.assertEqual([], self.season_matches_parser.received)

    def test_rejects_an_event_of_another_league_without_calling_any_parser(self):
        event = build_event(SEASON_MATCHES_EVENT_NAME, league="nba")

        with self.assertRaisesRegex(LeagueMismatch, "'fake_league'.*'nba'.*'season_matches'"):
            self.dispatcher.parse_event(event)

        self.assertEqual([], self.season_matches_parser.received)

    def test_league_mismatch_carries_the_expected_league_and_the_event(self):
        event = build_event(SEASON_MATCHES_EVENT_NAME, league="nba")

        with self.assertRaises(LeagueMismatch) as context:
            self.dispatcher.parse_event(event)

        self.assertEqual("fake_league", context.exception.expected_league)
        self.assertIs(event, context.exception.event)

    def test_rejects_an_event_type_without_a_registered_parser(self):
        with self.assertRaisesRegex(ParserNotFound, "'player_info'.*'fake_league'"):
            self.dispatcher.parse_event(build_event("player_info"))

    def test_checks_the_league_before_looking_for_the_parser(self):
        with self.assertRaises(LeagueMismatch):
            self.dispatcher.parse_event(build_event("player_info", league="nba"))


class TestEuroleagueEventParserDispatcher(unittest.TestCase):

    def setUp(self):
        self.dispatcher = EuroleagueEventParserDispatcher()

    def test_handles_events_of_the_euroleague(self):
        self.assertEqual(EUROLEAGUE_SOURCE_IDENTIFIER, self.dispatcher.league)

    def test_has_a_season_matches_parser_registered(self):
        self.assertIsInstance(self.dispatcher.event_dict[SEASON_MATCHES_EVENT_NAME], SeasonMatchesParser)

    def test_every_registered_parser_is_indexed_by_its_own_event_type(self):
        for event_type, parser in self.dispatcher.event_dict.items():
            self.assertEqual(event_type, parser.event_type)

    def test_rejects_events_of_other_leagues(self):
        with self.assertRaises(LeagueMismatch):
            self.dispatcher.parse_event(build_event(SEASON_MATCHES_EVENT_NAME, league="nba"))

    def test_rejects_event_types_that_have_no_parser_yet(self):
        with self.assertRaises(ParserNotFound):
            self.dispatcher.parse_event(build_event(TEAM_INFORMATION_EVENT_NAME, league=EUROLEAGUE_SOURCE_IDENTIFIER))


if __name__ == "__main__":
    unittest.main()
