"""
Puertos (Interfaces) para Repositorios - Dominio puro
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from api.domain.entities.planta import Planta
from api.domain.entities.telemetria import Telemetria
from api.domain.entities.sensor import Sensor


# ========== SENSOR REPOSITORY ==========
class SensorRepository(ABC):
    """Puerto para persistencia de sensores"""
    
    @abstractmethod
    async def guardar(self, sensor: Sensor) -> None:
        """Guarda o actualiza un sensor"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, sensor_id: UUID) -> Optional[Sensor]:
        """Obtiene un sensor por su ID"""
        pass
    
        """Elimina un sensor (soft/hard delete según dominio)"""
        pass
    #obtener metricas agregadas
    @abstractmethod
    async def obtener_por_planta(self, planta_id: UUID)-> List[Sensor]:
        """Obtiene todos los sensores asociados a una planta específica"""
        pass


# ========== TELEMETRIA REPOSITORY ==========
class TelemetriaRepository(ABC):
    """Puerto para persistencia de telemetrías"""
    
    @abstractmethod
    async def guardar(self, telemetria: Telemetria) -> None:
        """Guarda un registro de telemetría"""
        pass
    
    @abstractmethod
    async def guardar_lote(self, telemetrias: List[Telemetria]) -> None:
        """Guarda múltiples telemetrías de forma optimizada"""
        pass
        
    @abstractmethod
    async def obtener_ultima(self, sensor_id: UUID) -> Optional[Telemetria]:
        """Obtiene la última telemetría de un sensor"""
        pass

    @abstractmethod
    async def obtener_por_sensor(
        self, 
        sensor_id: UUID, 
        limite: int = 100,
        orden: str = "ASC",              
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> List[Telemetria]:
        """Obtiene telemetrías de un sensor con filtros"""
        pass
    
    @abstractmethod
    async def obtener_por_id(self, telemetria_id: UUID) -> Optional[Telemetria]:
        """Obtiene una telemetría por su ID"""
        pass
    # para cadena de integridad
    @abstractmethod 
    async def obtener_ultimo_hash(
            self,
            sensor_id: UUID
        ) -> Optional[str]:
          pass

# ========== PLANTA REPOSITORY ==========
class PlantaRepository(ABC):
    @abstractmethod
    async def guardar(self, planta: Planta) -> None:
        pass

    @abstractmethod
    async def obtener_por_id(self, id: UUID) -> Optional[Planta]:
        pass

    @abstractmethod
    async def obtener_todos(self) -> List[Planta]:
        pass
# cubre: hash encadenado, métricas, auditoría, lectura histórica, obtener ultimohash

# Elimine algunas porque parecia un DAO. Demasiado rico para hexagonal. Mejor menos acoplamiento. servicios mas expresivos.