from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from api.domain.events.sensor_events import SensorCreado, SensorEstadoCambiado
from domain.entities.telemetria import Telemetria
from enum import Enum

class TipoSensor(str, Enum):
    TEMPERATURA = "temperatura"
    PRESION = "presion"
    HUMEDAD = "humedad"
    VIBRACION = "vibracion"
    CAUDAL = "caudal"


@dataclass
class Sensor:
    """
    Entidad de dominio: Sensor industrial
    """
    id: UUID
    planta_id: UUID
    nombre: str
    tipo: TipoSensor
    unidad: str
    activo: bool = True

    # =========================
    # FACTORY
    # =========================
    @staticmethod
    def crear(
        planta_id: UUID,
        nombre: str,
        tipo: TipoSensor,
        unidad: str,
    ) -> "Sensor":
        return Sensor(
            id=uuid4(),
            planta_id=planta_id,
            nombre=nombre,
            tipo=tipo,
            unidad=unidad,
            activo=True,
        )
    # =========================
    # VALIDACIONES
    # =========================
    def _validar_valor(self, valor: float) -> None:
        if self.tipo == TipoSensor.TEMPERATURA and valor < -273.15:
            raise ValueError("Temperatura menor al cero absoluto")

        if self.tipo == TipoSensor.HUMEDAD and not (0 <= valor <= 100):
            raise ValueError("Humedad fuera de rango (0-100%)")

        if self.tipo in (
            TipoSensor.PRESION,
            TipoSensor.VIBRACION,
            TipoSensor.CAUDAL,
        ) and valor < 0:
            raise ValueError(f"{self.tipo.value} no puede ser negativo")
    
    def puede_registrar_lectura(self) -> bool:
        """Verifica si el sensor puede registrar datos"""
        return self.activo
 
    # =========================
    # ESTADO
    # =========================
    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    # =========================
    # EVENTOS DE DOMINIO
    # =========================
    def to_creado_event(self) -> SensorCreado:
        return SensorCreado(
            sensor_id=self.id,
            planta_id=self.planta_id,
            nombre=self.nombre,
            tipo=self.tipo,
            unidad=self.unidad,
        )

    def to_estado_cambiado_event(self, motivo: str) -> SensorEstadoCambiado:
        return SensorEstadoCambiado(
            sensor_id=self.id,
            activo=self.activo,
            motivo=motivo,
        )

  