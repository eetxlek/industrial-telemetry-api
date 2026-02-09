"""
Entidad Telemetria - Dominio puro con integridad blockchain-like
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import hashlib

#Entidad  que firma y encadena. Es el ledger o libro mayor
@dataclass
class Telemetria:
    """
    Representa un registro de telemetría con integridad de datos
    usando hashing encadenado similar a blockchain
    """
    id: UUID               #id unica
    sensor_id: UUID        #ref a padre
    valor: float           #dato crudo
    timestamp: datetime
    payload_hash: str      #estado complejo
    previous_hash: str     #estado complejo
    
    @property
    def fingerprint(self) -> str:
        """Alias semántico para el hash del payload"""
        return self.payload_hash
    
    #Tiene comportamiento de dominio, metodos estaticos
    # tiene logica de negocio (verifica integridad)
    # Factory thethod, garantiza encapsulacion hash
    @staticmethod
    def calcular_hash(
        sensor_id: UUID,
        valor: float,
        timestamp: datetime,
        previous_hash: str
    ) -> str:
        """
        Calcula el hash del payload usando SHA256
        payload_hash = SHA256(sensor_id + valor + timestamp + previous_hash)  --> .4f asegura que el hash sea determinista
        """
        payload = f"{sensor_id}{valor:.4f}{timestamp.isoformat()}{previous_hash}"
        return hashlib.sha256(payload.encode()).hexdigest()
    
    @staticmethod
    def crear(
        sensor_id: UUID,
        valor: float,
        timestamp: datetime,
        previous_hash: str = "0"
    ) -> 'Telemetria':
        """
        Factory method para crear un nuevo registro de telemetría
        con hash calculado automáticamente
        """
        payload_hash = Telemetria.calcular_hash(
            sensor_id, valor, timestamp, previous_hash
        )
        
        return Telemetria(
            id=uuid4(),
            sensor_id=sensor_id,
            valor=valor,
            timestamp=timestamp,
            payload_hash=payload_hash,
            previous_hash=previous_hash
        )
    
    def verificar_integridad(self) -> bool:
        """Verifica que el hash calculado coincida con el almacenado"""
        hash_calculado = self.calcular_hash(
            self.sensor_id,
            self.valor,
            self.timestamp,
            self.previous_hash
        )
        return hash_calculado == self.payload_hash
    