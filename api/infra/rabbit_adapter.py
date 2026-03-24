"""
Implementación concreta de EventPublisher usando RabbitMQ
"""
import json
import asyncio
from typing import Optional
import aio_pika
from aio_pika import ExchangeType

from api.application.ports.event_publisher import EventPublisher
from api.domain.events.base import DomainEvent

# implementacion infra de rabbit para el puerto event.publicar
class RabbitMQEventPublisher(EventPublisher):
    """Implementación concreta usando RabbitMQ para publicación de eventos"""
    
    def __init__(
        self,
        connection_string: str,
        exchange_name: str = "telemetria_events"             #domain events
    ):

        self.connection_string = connection_string
        self.exchange_name = exchange_name      
        self.connection: Optional[aio_pika.RobustConnection] = None   # maneja cortes de conexion
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        
        # Para manejo de errores y reintentos. Evita multiples conexiones si llegan eventos a la vez
        self._connection_lock = asyncio.Lock()
    
    async def connect(self):
        if self.connection:
            return

        self.connection = await aio_pika.connect_robust(self.connection_string)
        self.channel = await self.connection.channel()
        
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True
        )
    
    async def disconnect(self) -> None:
        """Cierra la conexión con RabbitMQ"""
        async with self._connection_lock:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
            
            if self.connection and not self.connection.is_closed: #evita doble conexion
                await self.connection.close()
   
            print("🔌 Desconectado de RabbitMQ")
    #recibe domainevent
    async def publicar(self, event: DomainEvent) -> None:
        await self.connect()

        routing_key = event.__class__.__name__   
        body = json.dumps(event.to_dict()).encode("utf-8")

        message = aio_pika.Message(
            body=body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        await self.exchange.publish(
            message,
            routing_key=routing_key  #   routing_key = event.__class__.__name__  # TelemetriaRegistrada #  f"telemetria.{event.event_type}"

        )

   