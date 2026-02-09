# domain/events/telemetria_events.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.telemetria import Telemetria
from domain.events.base import DomainEvent

#Evento
@dataclass(frozen=True)
class TelemetriaRegistrada (DomainEvent):
    telemetria_id: UUID
    sensor_id: UUID
    valor: float
    timestamp: datetime
    payload_hash: str
    previous_hash: str
  ## Hereda automáticamente event_id y occurred_at de DomainEvent

    @classmethod
    def from_entity(cls, telemetria: 'Telemetria'):
            return cls(
                telemetria_id=telemetria.id,
                sensor_id=telemetria.sensor_id,
                valor=telemetria.valor,
                timestamp=telemetria.timestamp,
                payload_hash=telemetria.payload_hash,
                previous_hash=telemetria.previous_hash
            )