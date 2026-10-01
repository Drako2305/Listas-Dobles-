import json
import tempfile
import unittest
from pathlib import Path

from app.models.treatment_event import TreatmentEvent
from app.services.timeline_service import TimelineService
from app.storage.json_timeline_repository import JsonTimelineRepository


def valid_fields(title: str = "Condition survey") -> dict[str, str]:
    return {
        "recorded_at": "2026-09-24T13:40",
        "title": title,
        "location": "Wet room",
        "conservator": "Mara Ellis",
        "treatment": "Recorded the current condition.",
        "materials": "",
        "notes": "",
    }


class TimelineServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.data_file = Path(self.temporary_directory.name) / "timeline.json"
        self.service = TimelineService(JsonTimelineRepository(self.data_file))

    def test_create_at_index_list_in_reverse_and_restore_from_disk(self) -> None:
        first = self.service.create_event(valid_fields("First"), 0)
        last = self.service.create_event(valid_fields("Last"), 1)
        middle = self.service.create_event(valid_fields("Middle"), 1)

        self.assertEqual(
            [event.title for event in self.service.list_events()],
            ["First", "Middle", "Last"],
        )
        self.assertEqual(
            [event.title for event in self.service.list_events(reverse=True)],
            ["Last", "Middle", "First"],
        )
        self.assertEqual(len({first.id, middle.id, last.id}), 3)
        restored = TimelineService(JsonTimelineRepository(self.data_file))
        self.assertEqual(
            [event.title for event in restored.list_events()],
            ["First", "Middle", "Last"],
        )

    def test_update_and_delete_event(self) -> None:
        event = self.service.create_event(valid_fields())
        updated = self.service.update_event(event.id, {"title": "Updated survey"})
        self.assertEqual(updated.title, "Updated survey")
        self.assertEqual(self.service.delete_event(event.id).id, event.id)
        self.assertEqual(self.service.list_events(), [])

    def test_invalid_event_and_missing_id_are_reported(self) -> None:
        with self.assertRaisesRegex(ValueError, "Title is required"):
            self.service.create_event(valid_fields(title=" "))
        with self.assertRaises(KeyError):
            self.service.delete_event("missing")

    def test_repository_rejects_malformed_json(self) -> None:
        self.data_file.write_text("{not-json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            JsonTimelineRepository(self.data_file).load()

    def test_saved_records_can_be_loaded(self) -> None:
        event = TreatmentEvent.create(valid_fields())
        self.data_file.write_text(json.dumps([event.to_dict()]), encoding="utf-8")
        self.assertEqual(
            JsonTimelineRepository(self.data_file).load()[0].id,
            event.id,
        )


if __name__ == "__main__":
    unittest.main()
