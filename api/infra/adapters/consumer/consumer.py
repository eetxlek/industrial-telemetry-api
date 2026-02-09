# infra/adapters/events/consumer.py
import asyncio
from aio_pika import connect_robust, IncomingMessage
import json

#hay que instalar pika

class TelemetriaConsumer:
    """Consume eventos de telemetría y ejecuta acciones"""
    
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.handlers = {
            "telemetria.registrada": self._handle_telemetria_registrada,
            "sensor.creado": self._handle_sensor_creado,
        }
    
    async def start(self):
        """Inicia el consumidor"""
        connection = await connect_robust(self.rabbitmq_url)
        channel = await connection.channel()
        
        # Declarar queue
        queue = await channel.declare_queue("telemetria_events", durable=True)
        
        # Consumir mensajes
        await queue.consume(self._process_message)
        
        print("✅ Consumidor de eventos iniciado")
        await asyncio.Future()  # Run forever
    
    async def _process_message(self, message: IncomingMessage):
        """Procesa cada mensaje recibido"""
        async with message.process():
            try:
                event_data = json.loads(message.body.decode())
                event_type = event_data.get("event_type")
                
                handler = self.handlers.get(event_type)
                if handler:
                    await handler(event_data)
                else:
                    print(f"⚠️ Evento desconocido: {event_type}")
                    
            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")
    
    async def _handle_telemetria_registrada(self, event: dict):
        """Handler para TelemetriaRegistrada"""
        print(f"📊 Nueva telemetría: {event['telemetria_id']}")
        
        # 1. Actualizar dashboard en tiempo real (WebSocket)
        await self._notify_dashboard(event)
        
        # 2. Verificar si requiere alerta
        await self._check_alertas(event)
        
        # 3. Actualizar cache de métricas
        await self._update_metrics_cache(event)
    
    async def _handle_sensor_creado(self, event: dict):
        """Handler para SensorCreadoEvent"""
        print(f"🔧 Nuevo sensor: {event['sensor_id']}")
        
        # 1. Configurar alertas por defecto
        await self._setup_default_alerts(event)
        
        # 2. Notificar administradores
        await self._notify_admins(event)
    
    async def _notify_dashboard(self, event: dict):
        """Envía actualización a dashboards vía WebSocket"""
        # Implementar con WebSocket manager
        pass
    
    async def _check_alertas(self, event: dict):
        """Verifica si el valor dispara alguna alerta"""
        valor = event.get("valor")
        sensor_id = event.get("sensor_id")
        
        # Obtener reglas de alerta del sensor
        # Si valor fuera de rango → enviar alerta
        pass
    
    async def _update_metrics_cache(self, event: dict):
        """Actualiza cache de métricas en Redis"""
        # Actualizar promedio móvil, min/max del día, etc.
        pass


# Script para ejecutar el consumidor
# consumer_main.py
if __name__ == "__main__":
    consumer = TelemetriaConsumer("amqp://guest:guest@localhost/")
    asyncio.run(consumer.start())