"""
Repositorio PostgreSQL para Telemetría
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, select, desc, func, and_

from domain.entities.telemetria import Telemetria
from application.ports.repositories import TelemetriaRepository
from ..models import TelemetriaModel


class PostgresTelemetriaRepository(TelemetriaRepository):
    """Implementación concreta usando PostgreSQL"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def guardar(self, telemetria: Telemetria) -> None:
        """Guarda una telemetría"""
        telemetria_dict = {
            "id": telemetria.id,
            "sensor_id": telemetria.sensor_id,
            "valor": telemetria.valor,
            "timestamp": telemetria.timestamp,
            "payload_hash": telemetria.payload_hash,
            "previous_hash": telemetria.previous_hash
        }
        
        # Verificar si existe
        stmt = select(TelemetriaModel).where(TelemetriaModel.id == telemetria.id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Actualizar (raro pero posible)
            existing.valor = telemetria.valor
            existing.timestamp = telemetria.timestamp
            existing.payload_hash = telemetria.payload_hash
            existing.previous_hash = telemetria.previous_hash
        else:
            # Insertar
            telemetria_db = TelemetriaModel(**telemetria_dict)
            self.session.add(telemetria_db)
        
        #  await self.session.commit()  # <--- NO commit aquí, la gestion de commit en service.
    
    async def guardar_lote(self, telemetrias: List[Telemetria]) -> None:
        """Bulk insert optimizado en vez de commit en cada"""
        telemetrias_dict = [
            {
                "id": t.id,
                "sensor_id": t.sensor_id,
                "valor": t.valor,
                "timestamp": t.timestamp,
                "payload_hash": t.payload_hash,
                "previous_hash": t.previous_hash
            }
            for t in telemetrias
        ]
        
        # Bulk insert de SQLAlchemy (más rápido)
        await self.session.execute(
            insert(TelemetriaModel),
            telemetrias_dict
        )
    
    async def obtener_ultima(self, sensor_id: UUID) -> Optional[Telemetria]:
        """Obtiene la última telemetría de un sensor"""
        stmt = (
            select(TelemetriaModel)
            .where(TelemetriaModel.sensor_id == sensor_id)
            .order_by(desc(TelemetriaModel.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        telemetria_db = result.scalar_one_or_none()
        
        if not telemetria_db:
            return None
        
        return self._to_entity(telemetria_db)
    
    async def obtener_por_id(self, telemetria_id: UUID) -> Optional[Telemetria]:
        stmt = select(TelemetriaModel).where(TelemetriaModel.id == telemetria_id)
        result = await self.session.execute(stmt)
        telemetria_db = result.scalar_one_or_none()
        if not telemetria_db:
            return None
        return self._to_entity(telemetria_db)

    async def obtener_ultimo_hash(self, sensor_id: UUID) -> str:
        """Obtiene el hash del último registro de un sensor con undice sensor_id"""
        stmt = (
            select(TelemetriaModel.payload_hash)                   # solo pide esa columna, ligero  -> camino rapido para escritura
            .where(TelemetriaModel.sensor_id == sensor_id)
            .order_by(desc(TelemetriaModel.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        ultimo_hash = result.scalar_one_or_none()
        
        return ultimo_hash if ultimo_hash else "0"

    #obtiene ULTIMIAS METRICAS muchos mas datos para usar solo uno. Mas lento y consume más  ---> para auditoria
    async def obtener_por_sensor(
        self, 
        sensor_id: UUID, 
        limite: int = 100,
        orden: str = "DESC",     #para el dashboard, ver lo mas reciente
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> List[Telemetria]:
        """Obtiene telemetrías de un sensor con filtros"""
        
        # Construir condiciones
        condiciones = [TelemetriaModel.sensor_id == sensor_id]
        
        if desde:
            condiciones.append(TelemetriaModel.timestamp >= desde)
        if hasta:
            condiciones.append(TelemetriaModel.timestamp <= hasta)
        
        # Elegimos el criterio de ordenación dinámicamente
        order_criteria = desc(TelemetriaModel.timestamp) if orden.upper() == "DESC" else asc(TelemetriaModel.timestamp)

        stmt = (
            select(TelemetriaModel)
            .where(and_(*condiciones))
            .order_by(order_criteria)
            .limit(limite)
        )
        
        result = await self.session.execute(stmt)
        telemetrias_db = result.scalars().all()
        
        return [self._to_entity(t) for t in telemetrias_db]
    
    def _to_entity(self, telemetria_db: TelemetriaModel) -> Telemetria:
        """Convierte modelo SQLAlchemy a entidad de dominio"""
        return Telemetria(
            id=telemetria_db.id,
            sensor_id=telemetria_db.sensor_id,
            valor=telemetria_db.valor,
            timestamp=telemetria_db.timestamp,
            payload_hash=telemetria_db.payload_hash,
            previous_hash=telemetria_db.previous_hash
        )
   