from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from api.application.services.telemetria_service import TelemetriaService

@pytest.mark.asyncio
async def test_registro_telemetria_orquestacion():
    # Mocks
    mock_sensor_repo = AsyncMock()
    mock_telemetria_repo = AsyncMock()
    mock_event_bus = AsyncMock()
    mock_session = AsyncMock()
    
    # Configurar mocks
    mock_sensor_repo.obtener_por_id.return_value = Mock(activo=True)
    mock_telemetria_repo.obtener_ultimo_hash.return_value = "0"
    
    service = TelemetriaService(
        sensor_repo=mock_sensor_repo,
        telemetria_repo=mock_telemetria_repo,
        event_publisher=mock_event_bus,
        session=mock_session
    )
    
    # Ejecutar
    await service.registrar_lectura(sensor_id=uuid4(), valor=22.4)
    
    # Verificar
    mock_telemetria_repo.guardar.assert_awaited_once()
    mock_event_bus.publicar.assert_awaited_once()
    mock_session.commit.assert_awaited_once()