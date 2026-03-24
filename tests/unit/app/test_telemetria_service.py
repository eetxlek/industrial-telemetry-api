from unittest.mock import Mock
from uuid import uuid4
from api.application.services.telemetria_service import TelemetriaService

def test_registro_telemetria_orquestacion():
    # Mocks de los adaptadores de infra (puertos)
    mock_repo = Mock()
    mock_bus = Mock()

    # servicio real pero con mocks, patron dependency injection
    service = TelemetriaService(repository=mock_repo, event_bus=mock_bus) 
    
    # Ejecutamos la acción real
    service.registrar_lectura(sensor_id=uuid4(), valor=22.4)
    
    # Verificamos que se llamó al repo para guardar
    assert mock_repo.save.called
    # Verificamos que se publicó un evento
    assert mock_bus.publish.called

# test que verifica que service actua correctamente de orquestador (coge dato y pasa a dominio)