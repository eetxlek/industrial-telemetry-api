# infra/events/publisher_factory.py      DECISION DE LA INFRA
import os
from api.infra.logging_publisher import LoggingEventPublisher
from api.infra.rabbit_adapter import RabbitMQEventPublisher
from application.ports.event_publisher import EventPublisher

class EventPublisherFactory:

    @staticmethod
    def create_publisher() -> EventPublisher:
        backend = os.getenv("EVENT_BACKEND", "logging")
        #conectar productor de telemetria a mediador que distribuye mensaje con clave de enrutamiento usando lib. se puede iniciar usando Docker.
        #productor conecta con consumidor(rabbit medio, un bus que gestiona cola de eventos publicados y los distribuye a consumidores suscritos)
        if backend == "rabbitmq":
            #evita exchange harcodeado
            return RabbitMQEventPublisher(
                connection_string=os.getenv("RABBITMQ_URL"),
                exchange_name=os.getenv("RABBITMQ_EXCHANGE", "domain_events")
            )

        return LoggingEventPublisher()
