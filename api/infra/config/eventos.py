# infraestructura/configuracion/eventos.py

from typing import Optional
import logging
from abc import ABC, abstractmethod

from api.infra.config.settings import settings

logger = logging.getLogger(__name__)

class EventBusConfig(ABC):
    # mismo canal,pero UI espera objetos diferentes.
    """Configuración base para bus de eventos"""
    
    @abstractmethod
    def get_producer(self):
        pass
    
    @abstractmethod
    def get_consumer(self):
        pass

    @abstractmethod
    def close(self):
        pass

class KafkaConfig(EventBusConfig):
    """Configuración para Apache Kafka"""
    
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = settings.KAFKA_TOPIC_TELEMETRIA
        self.consumer_group = settings.KAFKA_CONSUMER_GROUP
        self._producer = None
        self._consumer = None
    
    def get_producer(self):
        """Lazy loading del producer"""
        if self._producer is None:
            try:
                from kafka import KafkaProducer
                import json
                
                self._producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers.split(','),
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',  # Confirmación de todas las réplicas
                    retries=3,
                    max_in_flight_requests_per_connection=1
                )
                logger.info(f"Kafka Producer conectado a {self.bootstrap_servers}")
            except Exception as e:
                logger.error(f"Error al crear Kafka Producer: {e}")
                raise
        
        return self._producer
    
    def get_consumer(self):
        """Lazy loading del consumer"""
        if self._consumer is None:
            try:
                from kafka import KafkaConsumer
                import json
                
                self._consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers.split(','),
                    group_id=self.consumer_group,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='earliest',
                    enable_auto_commit=True
                )
                logger.info(f"Kafka Consumer conectado al topic {self.topic}")
            except Exception as e:
                logger.error(f"Error al crear Kafka Consumer: {e}")
                raise
        
        return self._consumer
    
    def close(self):
        """Cierra conexiones"""
        if self._producer:
            self._producer.close()
        if self._consumer:
            self._consumer.close()
        logger.info("Kafka cerrado correctamente")

class RabbitMQConfig(EventBusConfig):
    """Configuración para RabbitMQ"""
    
    def __init__(self):
        self.url = settings.RABBITMQ_URL
        self.exchange = settings.RABBITMQ_EXCHANGE
        self.queue = settings.RABBITMQ_QUEUE
        self._connection = None
        self._channel = None
    
    def get_connection(self):
        """Obtiene conexión a RabbitMQ"""
        if self._connection is None or self._connection.is_closed:
            try:
                import pika
                
                parameters = pika.URLParameters(self.url)
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                
                # Declarar exchange y queue
                self._channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type='topic',
                    durable=True
                )
                self._channel.queue_declare(queue=self.queue, durable=True)
                self._channel.queue_bind(
                    queue=self.queue,
                    exchange=self.exchange,
                    routing_key='telemetria.#'
                )
                
                logger.info(f"RabbitMQ conectado: {self.exchange}")
            except Exception as e:
                logger.error(f"Error al conectar con RabbitMQ: {e}")
                raise
        
        return self._connection
    
    def get_producer(self):
        """Retorna el canal para publicar"""
        self.get_connection()
        return self._channel
    
    def get_consumer(self):
        """Retorna el canal para consumir"""
        self.get_connection()
        return self._channel
    
    def close(self):
        """Cierra conexión"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
        logger.info("RabbitMQ cerrado correctamente")

# Factory para obtener configuración según entorno
def get_event_bus_config() -> EventBusConfig:
    """
    Factory que retorna la configuración correcta
    según las variables de entorno
    """
    if settings.KAFKA_BOOTSTRAP_SERVERS:
        return KafkaConfig()
    elif settings.RABBITMQ_URL:
        return RabbitMQConfig()
    else:
        logger.warning("No hay configuración de bus de eventos. Usando mock.")
        return Optional[EventBusConfig]  # O una implementación Mock para desarrollo

event_bus_config = get_event_bus_config()