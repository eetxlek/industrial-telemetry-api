"""
Exportar repositorios
"""
from .sensor_repository import PostgresSensorRepository
from .telemetria_repository import PostgresTelemetriaRepository

__all__ = [
    "PostgresSensorRepository",
    "PostgresTelemetriaRepository"
]