"""
Dependencias para inyección en FastAPI
"""
from typing import AsyncGenerator
from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.infra.adapters.persistance.repos.planta_repo import SQLPlantaRepository
from api.infra.adapters.persistance.repos.sensor_repo import PostgresSensorRepository
from api.infra.adapters.persistance.repos.telemetria_repo import PostgresTelemetriaRepository
from api.infra.adapters.rest.schemas.metrica import MetricaQueryParams
from api.infra.adapters.rest.schemas.sensor import SensorQueryParams
from api.infra.adapters.rest.schemas.telemetria import TelemetriaQueryParams
from api.infra.publisher_factory import EventPublisherFactory
from application.ports.repositories import SensorRepository, TelemetriaRepository
from application.ports.event_publisher import EventPublisher
from application.services.auditoria_service import AuditoriaService
from application.services.planta_service import PlantaService
from application.services.sensor_service import SensorService
from application.services.telemetria_service import TelemetriaService


#INYECCIONES PARA FASTAPI

# ========== DATABASE SESSION ==========

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtiene sesión de base de datos"""
    async for session in get_db():
        yield session


# ========== REPOSITORIES ==========

async def get_sensor_repository(db: AsyncSession = Depends(get_db)) -> SensorRepository:
    """Obtiene repositorio de sensores"""
    return PostgresSensorRepository(db)


async def get_telemetria_repository(db: AsyncSession = Depends(get_db)) -> TelemetriaRepository:
    """Obtiene repositorio de telemetrías"""
    return PostgresTelemetriaRepository(db)


# ========== EVENT PUBLISHER ==========

async def get_event_publisher(request: Request) -> EventPublisher:
    """Obtiene publisher de eventos"""
    return request.app.state.event_publisher


# ========== SERVICES ==========

def get_sensor_service(
    sensor_repo: SensorRepository = Depends(get_sensor_repository),
    telemetria_repo: TelemetriaRepository = Depends(get_telemetria_repository),
    event_publisher: EventPublisher = Depends(get_event_publisher)
) -> SensorService:
    """Factory para SensorService"""
    return SensorService(sensor_repo, telemetria_repo, event_publisher)

def get_auditoria_service(session: AsyncSession = Depends(get_db)) -> AuditoriaService:
    # 1. Instanciamos los adaptadores (repositorios)
    telemetria_repo = TelemetriaRepository(session)
    sensor_repo = SensorRepository(session)
    
    # 2. Inyectamos los repositorios en el servicio
    return AuditoriaService(
        telemetria_repo=telemetria_repo,
        sensor_repo=sensor_repo
    )

async def get_planta_service(session: AsyncSession = Depends(get_db)):
    repo = SQLPlantaRepository(session)
    # IMPORTANTE: El nombre del argumento aquí debe coincidir con el del __init__
    return PlantaService(planta_repo=repo)


def get_telemetria_service(
    sensor_repo: SensorRepository = Depends(get_sensor_repository),
    telemetria_repo: TelemetriaRepository = Depends(get_telemetria_repository),
    event_publisher: EventPublisher = Depends(get_event_publisher),
    db_session: AsyncSession = Depends(get_db)
) -> TelemetriaService:
    """Factory para TelemetriaService"""
    return TelemetriaService(sensor_repo, telemetria_repo, event_publisher, db_session)

# ========== QUERY PARAMETERS ==========

def get_sensor_query_params(
    planta_id: str = Query(None, description="ID de la planta"),
    tipo: str = Query(None, description="Tipo de sensor"),
    activo: bool = Query(None, description="Estado del sensor"),
    nombre_contiene: str = Query(None, description="Texto contenido en el nombre"),
    pagina: int = Query(1, ge=1, description="Número de página"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página")
) -> SensorQueryParams:
    """Convierte query params a SensorQueryParams"""
    from uuid import UUID
    
    return SensorQueryParams(
        planta_id=UUID(planta_id) if planta_id else None,
        tipo=tipo,
        activo=activo,
        nombre_contiene=nombre_contiene,
        pagina=pagina,
        por_pagina=por_pagina
    )


def get_telemetria_query_params(
    sensor_id: str = Query(None, description="ID del sensor"),
    desde: str = Query(None, description="Fecha de inicio (YYYY-MM-DDTHH:MM:SS)"),
    hasta: str = Query(None, description="Fecha de fin (YYYY-MM-DDTHH:MM:SS)"),
    valor_min: float = Query(None, description="Valor mínimo"),
    valor_max: float = Query(None, description="Valor máximo"),
    pagina: int = Query(1, ge=1, description="Número de página"),
    por_pagina: int = Query(50, ge=1, le=1000, description="Elementos por página")
) -> TelemetriaQueryParams:
    """Convierte query params a TelemetriaQueryParams"""
    from uuid import UUID
    from datetime import datetime
    
    return TelemetriaQueryParams(
        sensor_id=UUID(sensor_id) if sensor_id else None,
        desde=datetime.fromisoformat(desde) if desde else None,
        hasta=datetime.fromisoformat(hasta) if hasta else None,
        valor_min=valor_min,
        valor_max=valor_max,
        pagina=pagina,
        por_pagina=por_pagina
    )


def get_metrica_query_params(
    sensor_id: str = Query(..., description="ID del sensor"),
    desde: str = Query(None, description="Fecha de inicio (YYYY-MM-DDTHH:MM:SS)"),
    hasta: str = Query(None, description="Fecha de fin (YYYY-MM-DDTHH:MM:SS)"),
    intervalo: str = Query(None, description="Intervalo (hour, day, week, month)")
) -> MetricaQueryParams:
    """Convierte query params a MetricaQueryParams"""
    from uuid import UUID
    from datetime import datetime
    
    return MetricaQueryParams(
        sensor_id=UUID(sensor_id),
        desde=datetime.fromisoformat(desde) if desde else None,
        hasta=datetime.fromisoformat(hasta) if hasta else None,
        intervalo=intervalo
    )


