from threading import RLock

from app.models.doubly_linked_list import DoublyLinkedList
from app.models.treatment_event import TreatmentEvent
from app.storage.json_timeline_repository import JsonTimelineRepository


class TimelineService:
    def __init__(self, repository: JsonTimelineRepository) -> None:
        self._repository = repository
        self._events: DoublyLinkedList[TreatmentEvent] = DoublyLinkedList()
        self._lock = RLock()
        for event in repository.load():
            self._events.append(event)

    def list_events(self, reverse: bool = False) -> list[TreatmentEvent]:
        with self._lock:
            return list(reversed(self._events) if reverse else iter(self._events))

    def create_event(
        self,
        fields: dict[str, object],
        insertion_index: int | None = None,
    ) -> TreatmentEvent:
        with self._lock:
            index = len(self._events) if insertion_index is None else insertion_index
            if not isinstance(index, int) or isinstance(index, bool):
                raise ValueError("Insertion index must be an integer.")
            event = TreatmentEvent.create(fields)
            self._events.insert(index, event)
            self._save()
            return event

    def update_event(self, event_id: str, fields: dict[str, object]) -> TreatmentEvent:
        with self._lock:
            event = self._find_event(event_id)
            event.update(fields)
            self._save()
            return event

    def delete_event(self, event_id: str) -> TreatmentEvent:
        with self._lock:
            for index, event in enumerate(self._events):
                if event.id == event_id:
                    removed = self._events.remove(index)
                    self._save()
                    return removed
            raise KeyError(f"No timeline entry exists with id '{event_id}'.")

    def _find_event(self, event_id: str) -> TreatmentEvent:
        for event in self._events:
            if event.id == event_id:
                return event
        raise KeyError(f"No timeline entry exists with id '{event_id}'.")

    def _save(self) -> None:
        self._repository.save(list(self._events))
