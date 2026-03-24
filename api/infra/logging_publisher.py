# infra/events/logging_publisher.py
from dataclasses import asdict
import json
from api.application.ports.event_publisher import EventPublisher
from api.domain.events.base import DomainEvent

class LoggingEventPublisher(EventPublisher):

    # Este evento se mostrará en la consola justo despues del POST telemetria como objeto json, dict.  PARA DEV TEST
    async def publicar(self, event: DomainEvent) -> None:
        print("📣 EVENTO")
        
        payload = {
            "metadata": {
                "event_id": event.event_id,
                "type": event.event_type,
                "occurred_at": event.occurred_at.isoformat(),
            },
            "data": asdict(event) 
        }

        print(json.dumps(payload, default=str, indent=2))

    async def publicar_lote(self, events):
        for event in events:
            await self.publicar(event)
