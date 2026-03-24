"""
Repositorio PostgreSQL para Sensor
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from domain.entities.sensor import Sensor
from application.ports.repositories import SensorRepository
from ..models import SensorModel

class PostgresSensorRepository(SensorRepository):
    """Implementación concreta usando PostgreSQL"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def guardar(self, sensor: Sensor) -> None:
        """Guarda o actualiza un sensor"""
        # Convertir entidad a modelo
        sensor_dict = {
            "id": sensor.id,
            "planta_id": sensor.planta_id,
            "nombre": sensor.nombre,
            "tipo": sensor.tipo.value,
            "unidad": sensor.unidad,
            "activo": sensor.activo
        }
        
        # Verificar si existe
        stmt = select(SensorModel).where(SensorModel.id == sensor.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Actualizar
            await self.session.execute(
                update(SensorModel)
                .where(SensorModel.id == sensor.id)
                .values(**sensor_dict)
            )
        else:
            # Insertar
            sensor_db = SensorModel(**sensor_dict)
            self.session.add(sensor_db)

    # obtener sensor
    async def obtener_por_id(self, sensor_id: UUID) -> Optional[Sensor]:
        """Obtiene un sensor por su ID"""
        stmt = select(SensorModel).where(SensorModel.id == sensor_id)
        result = await self.session.execute(stmt)
        sensor_db = result.scalar_one_or_none()
        
        if not sensor_db:
            return None
        
        # Convertir modelo a entidad
        return self._to_entity(sensor_db) 

    #lista de sensores de planta
    async def obtener_por_planta(self, planta_id: UUID) -> List[Sensor]:
        """Obtiene todos los sensores de una planta"""
        stmt = select(SensorModel).where(SensorModel.planta_id == planta_id)
        result = await self.session.execute(stmt)
        sensores_db = result.scalars().all()
        
        return [self._to_entity(sensor) for sensor in sensores_db]
    
    def _to_entity(self, sensor_db: SensorModel) -> Sensor:

        """Convierte modelo SQLAlchemy a entidad de dominio"""
        from domain.entities.sensor import Sensor, TipoSensor
        
        # Crear sensor (sin telemetrías por defecto)
        sensor = Sensor(
            id=sensor_db.id,
            planta_id=sensor_db.planta_id,
            nombre=sensor_db.nombre,
            tipo=TipoSensor(sensor_db.tipo.value),
            unidad=sensor_db.unidad,
            activo=sensor_db.activo
        )
        
        return sensor