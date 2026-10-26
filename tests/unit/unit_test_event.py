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

    def test_from_json_restores_an_event_stored_with_get_event(self):
        original = Event("raw response body", self.metadata, event_date=1700000000.5)

        restored = Event.from_json(original.get_event())

        self.assertEqual("raw response body", restored.event_string)
        self.assertEqual(self.metadata, restored.metadata)
        self.assertEqual(1700000000.5, restored.get_event_date())

    def test_from_json_keeps_the_raw_payload_untouched(self):
        xml = '<?xml version="1.0"?>\n<season code="E2023">\u00f1 "quoted"</season>'
        original = Event(xml, self.metadata, event_date=1.0)

        restored = Event.from_json(original.get_event())

        self.assertEqual(xml, restored.event_string)

    def test_from_json_keeps_a_json_payload_as_text(self):
        payload = '{"b":   2,  "a": [1,2]}'
        original = Event(payload, self.metadata, event_date=1.0)

        restored = Event.from_json(original.get_event())

        self.assertIsInstance(restored.event_string, str)
        self.assertEqual(payload, restored.event_string)

    def test_from_json_defaults_missing_event_params_to_empty(self):
        text = ('{"metadata": {"source_league": "euroleague", "event_type": "league_info", '
                '"data_format": "json"}, "event": "{}", "date": 1.0}')

        restored = Event.from_json(text)

        self.assertEqual({}, restored.get_event_params())

    def test_from_json_rejects_text_that_is_not_json(self):
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            Event.from_json("not json")

    def test_from_json_rejects_json_that_is_not_an_object(self):
        with self.assertRaisesRegex(ValueError, "expected a JSON object"):
            Event.from_json("[1, 2]")

    def test_from_json_rejects_envelope_without_date(self):
        text = ('{"metadata": {"source_league": "euroleague", "event_type": "team_info", '
                '"data_format": "json"}, "event": "{}"}')

        with self.assertRaisesRegex(ValueError, r"Incomplete event: missing \['date'\]"):
            Event.from_json(text)

    def test_from_json_rejects_metadata_without_required_fields(self):
        text = '{"metadata": {"source_league": "euroleague"}, "event": "{}", "date": 1.0}'

        with self.assertRaisesRegex(ValueError, "Incomplete event metadata: missing"):
            Event.from_json(text)

    def test_from_json_rejects_metadata_that_is_not_an_object(self):
        text = '{"metadata": "x", "event": "{}", "date": 1.0}'

        with self.assertRaisesRegex(ValueError, "metadata must be a JSON object"):
            Event.from_json(text)


if __name__ == "__main__":
    unittest.main()
