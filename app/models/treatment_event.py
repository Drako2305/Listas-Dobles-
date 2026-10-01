from dataclasses import asdict, dataclass
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class TreatmentEvent:
    id: str
    recorded_at: str
    title: str
    location: str
    conservator: str
    treatment: str
    materials: str
    notes: str

    @classmethod
    def create(cls, fields: dict[str, object]) -> "TreatmentEvent":
        cleaned = cls._validated_fields(fields)
        return cls(id=str(uuid4()), **cleaned)

    @classmethod
    def from_dict(cls, data: object) -> "TreatmentEvent":
        if not isinstance(data, dict):
            raise ValueError("Each saved timeline entry must be an object.")

        entry_id = data.get("id")
        if not isinstance(entry_id, str) or not entry_id.strip():
            raise ValueError("Each saved timeline entry must have an id.")

        cleaned = cls._validated_fields(data)
        return cls(id=entry_id, **cleaned)

    def update(self, fields: dict[str, object]) -> None:
        current = asdict(self)
        current.update({key: value for key, value in fields.items() if key != "id"})
        cleaned = self._validated_fields(current)
        for key, value in cleaned.items():
            setattr(self, key, value)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @staticmethod
    def _validated_fields(fields: dict[str, object]) -> dict[str, str]:
        required_field_limits = {
            "recorded_at": 160,
            "title": 160,
            "location": 160,
            "conservator": 160,
            "treatment": 5000,
        }
        optional_fields = ("materials", "notes")
        cleaned: dict[str, str] = {}

        for name, maximum_length in required_field_limits.items():
            value = fields.get(name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name.replace('_', ' ').capitalize()} is required.")
            value = value.strip()
            if len(value) > maximum_length:
                raise ValueError(
                    f"{name.replace('_', ' ').capitalize()} must be "
                    f"{maximum_length} characters or fewer."
                )
            cleaned[name] = value

        try:
            parsed_date = datetime.fromisoformat(cleaned["recorded_at"])
        except ValueError as error:
            raise ValueError("Recorded at must be a valid date and time.") from error
        cleaned["recorded_at"] = parsed_date.isoformat(timespec="minutes")

        for name in optional_fields:
            value = fields.get(name, "")
            if not isinstance(value, str):
                raise ValueError(f"{name.capitalize()} must be text.")
            value = value.strip()
            if len(value) > 5000:
                raise ValueError(f"{name.capitalize()} must be 5000 characters or fewer.")
            cleaned[name] = value

        return cleaned
