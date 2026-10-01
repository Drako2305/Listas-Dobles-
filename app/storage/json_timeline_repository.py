import json
from pathlib import Path

from app.models.treatment_event import TreatmentEvent


class JsonTimelineRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def load(self) -> list[TreatmentEvent]:
        if not self.file_path.exists():
            return []

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Timeline data is not valid JSON: {self.file_path}") from error

        if not isinstance(data, list):
            raise ValueError("Timeline data must be a JSON array.")
        return [TreatmentEvent.from_dict(item) for item in data]

    def save(self, events: list[TreatmentEvent]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.file_path.with_name(f".{self.file_path.name}.tmp")
        contents = json.dumps(
            [event.to_dict() for event in events],
            ensure_ascii=False,
            indent=2,
        )
        try:
            temporary_path.write_text(contents + "\n", encoding="utf-8")
            temporary_path.replace(self.file_path)
        finally:
            temporary_path.unlink(missing_ok=True)
