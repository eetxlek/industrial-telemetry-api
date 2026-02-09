"""
Modelos SQLAlchemy para persistencia
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, Index, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import enum
from domain.entities.planta import Planta
from infra.config.database import Base

#REALIDAD DE LA BASE DE DATOS
class TipoSensorDB(enum.Enum):
    """Tipos de sensores en base de datos"""
    TEMPERATURA = "temperatura"
    PRESION = "presion"
    HUMEDAD = "humedad"
    VIBRACION = "vibracion"
    CAUDAL = "caudal"


class SensorModel(Base):
    """Modelo SQLAlchemy para Sensor"""
    __tablename__ = "sensores"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    planta_id = Column(UUID(as_uuid=True), ForeignKey("plantas.id"), ondelete="RESTRICT",nullable=False)
    nombre = Column(String(200), nullable=False)
    tipo = Column(Enum(TipoSensorDB), nullable=False)
    unidad = Column(String(50), nullable=False)
    activo = Column(Boolean, nullable=False, server_default="true")
    
    # Relación con telemetrías
    telemetrias = relationship("TelemetriaModel", back_populates="sensor")
    #Con planta
    planta = relationship("PlantaModel", back_populates="sensores")  # <--- FIX

    __table_args__ = (
        Index('ix_sensores_planta_id', 'planta_id'),
        Index('ix_sensores_activo', 'activo'),
    )


class TelemetriaModel(Base):
    """Modelo SQLAlchemy para Telemetría"""
    __tablename__ = "telemetrias"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensores.id"), nullable=False)
    valor = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    payload_hash = Column(String(64), nullable=False, index=True)
    previous_hash = Column(String(64), nullable=False)
    
    # Relación inversa
    sensor = relationship("SensorModel", back_populates="telemetrias", lazy='noload')
    
    # Índices para búsquedas comunes
    __table_args__ = (
        Index('ix_telemetrias_sensor_timestamp', 'sensor_id', 'timestamp'),
        Index('ix_telemetrias_timestamp', 'timestamp'),
        Index('ix_telemetrias_payload_hash', 'payload_hash'),
    )

class PlantaModel(Base):
    __tablename__ = "plantas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(255), nullable=True)
    activa = Column(Boolean, default=True) 
    fecha_creacion = Column(DateTime, default=datetime.now(timezone.utc))

    # Relación con Sensores (Opcional, pero recomendada)
    # Esto permite hacer: mi_planta.sensores
    sensores = relationship("SensorModel", back_populates="planta")
    # Índice para búsquedas por nombre
    __table_args__ = (
        Index('ix_plantas_nombre', 'nombre'),
    )

   