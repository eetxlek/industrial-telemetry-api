# domain/events/sensor_events.py
from dataclasses import dataclass
from uuid import UUID
from domain.entities.sensor import TipoSensor

@dataclass(frozen=True)
class SensorCreado:
    sensor_id: UUID
    planta_id: UUID
    nombre: str
    tipo: TipoSensor
    unidad: str

@dataclass(frozen=True)
class SensorEstadoCambiado:
    sensor_id: UUID
    activo: bool
    motivo: str
