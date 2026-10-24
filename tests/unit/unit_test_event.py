import time
import unittest

from common.events.event import Event, EventMetadata


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.metadata = EventMetadata(
            source_league="euroleague",
            event_type="team_info",
            data_format="json",
            event_params={"team_id": "MAD"})

    def test_event_date_defaults_to_current_time(self):
        before = time.time()

        event = Event("raw response body", self.metadata)

        after = time.time()
        self.assertTrue(before <= event.get_event_date() <= after)

    def test_event_date_is_kept_when_given(self):
        event = Event("raw response body", self.metadata, event_date=1234.5)

        self.assertEqual(1234.5, event.get_event_date())


if __name__ == "__main__":
    unittest.main()
