import pytest
from uuid import uuid4
from datetime import datetime, timezone
from api.domain.entities.telemetria import Telemetria
from api.infra.adapters.persistance.repos.telemetria_repo import PostgresTelemetriaRepository

# Necesitas pytest-asyncio instalado
@pytest.mark.asyncio  
async def test_db_persistence_real(db_session):
    """
    Prueba de integración real contra Postgres
    """
    # 1. Preparación (Arrange)
    repo = PostgresTelemetriaRepository(session=db_session)
    sensor_id = uuid4()
    t = Telemetria.crear(sensor_id, 45.0, datetime.now(timezone.utc))
    
    # 2. Acción (Act)
    await repo.guardar(t)
    await db_session.commit() # Aseguramos que el dato se persiste
    
    # 3. Verificación (Assert)
    # Suponiendo que implementas 'obtener_por_id' en tu repo:
    db_record = await repo.obtener_por_id(t.id)
    
    assert db_record is not None
    assert db_record.payload_hash == t.payload_hash
    assert db_record.valor == 45.0