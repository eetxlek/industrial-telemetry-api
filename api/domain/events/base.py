from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import uuid

@dataclass(frozen=True)
class DomainEvent:
    event_id: str 
    occurred_at: datetime 

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.occurred_at:
            self.occurred_at = datetime.now(timezone.utc)

    @property
    def event_type(self) -> str:
        # Esto devuelve el nombre de la clase (ej: "TelemetriaRegistradaEvent")
        return self.__class__.__name__
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data["event_id"] = self.event_id
        data["occurred_at"] = self.occurred_at
        data["event_type"] = self.__class__.__name__
        return data