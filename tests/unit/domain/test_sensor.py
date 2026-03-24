import pytest
from uuid import uuid4
from api.domain.entities.sensor import Sensor, TipoSensor

def test_sensor_temperatura_valida_cero_absoluto():
    sensor = Sensor.crear(uuid4(), "Termómetro", TipoSensor.TEMPERATURA, "ºC")
    
    # Caso OK
    sensor._validar_valor(-10.0) # No debería lanzar nada
    
    # Caso Error: Debajo del cero absoluto
    with pytest.raises(ValueError, match="menor al cero absoluto"):
        sensor._validar_valor(-300.0)

def test_sensor_humedad_rango_valido():
    sensor = Sensor.crear(uuid4(), "Higrómetro", TipoSensor.HUMEDAD, "%")
    
    with pytest.raises(ValueError, match="fuera de rango"):
        sensor._validar_valor(105.0)