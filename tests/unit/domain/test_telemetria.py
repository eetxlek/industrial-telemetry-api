from datetime import datetime
from uuid import uuid4
from api.domain.entities.telemetria import Telemetria

def test_telemetria_blockchain_integrity():
    sensor_id = uuid4()
    ts = datetime.now()
    
    # Creamos el primer bloque (genesis)
    t1 = Telemetria.crear(sensor_id, 25.5, ts, "0")
    assert t1.verificar_integridad() is True
    
    # Creamos el segundo bloque encadenado al primero
    t2 = Telemetria.crear(sensor_id, 26.0, ts, t1.payload_hash)
    assert t2.previous_hash == t1.payload_hash
    assert t2.verificar_integridad() is True

def test_telemetria_detecta_manipulacion():
    t = Telemetria.crear(uuid4(), 10.0, datetime.now(), "0")
    # Manipulamos el valor maliciosamente
    t.valor = 999.0 
    assert t.verificar_integridad() is False