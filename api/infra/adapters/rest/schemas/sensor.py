"""
Schemas Pydantic para Sensores
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from domain.entities.sensor import TipoSensor


class TipoSensorEnum(str, Enum):
    """Enum para tipos de sensor en API"""
    TEMPERATURA = "temperatura"
    PRESION = "presion"
    HUMEDAD = "humedad"
    VIBRACION = "vibracion"
    CAUDAL = "caudal"


# ========== REQUEST SCHEMAS ==========

class SensorCreateRequest(BaseModel):
    """Schema para crear un sensor"""
    planta_id: UUID = Field(..., description="ID de la planta")
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre del sensor",
        example="Sensor Temperatura Reactor A"
    )
    tipo: TipoSensorEnum = Field(..., description="Tipo de sensor")
    unidad: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unidad de medida",
        example="°C"
    )
    
    @field_validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()
    
    @field_validator('unidad')
    def unidad_valida(cls, v):
        if not v.strip():
            raise ValueError('La unidad no puede estar vacía')
        return v.strip()


class SensorUpdateRequest(BaseModel):
    """Schema para actualizar un sensor"""
    nombre: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="Nuevo nombre del sensor"
    )
    unidad: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Nueva unidad de medida"
    )
    
    @field_validator('nombre')
    def nombre_no_vacio(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip() if v else v
    
    @field_validator('unidad')
    def unidad_valida(cls, v):
        if v is not None and not v.strip():
            raise ValueError('La unidad no puede estar vacía')
        return v.strip() if v else v


class SensorEstadoRequest(BaseModel):
    """Schema para cambiar estado de sensor"""
    activo: bool = Field(..., description="Nuevo estado del sensor")
    motivo: Optional[str] = Field(
        None,
        max_length=500,
        description="Motivo del cambio de estado"
    )


# ========== RESPONSE SCHEMAS ==========

class SensorBaseResponse(BaseModel):
    """Base para respuestas de sensor"""
    id: UUID
    planta_id: UUID
    nombre: str
    tipo: TipoSensorEnum
    unidad: str
    activo: bool
    fecha_creacion: Optional[datetime] = None


class SensorResponse(SensorBaseResponse):
    """Respuesta detallada de sensor"""
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_entity(cls, sensor) -> 'SensorResponse':
        """Crea response desde entidad de dominio"""
        return cls(
            id=sensor.id,
            planta_id=sensor.planta_id,
            nombre=sensor.nombre,
            tipo=TipoSensorEnum(sensor.tipo.value),
            unidad=sensor.unidad,
            activo=sensor.activo
            # Nota: La entidad no tiene fecha_creacion
        )


class SensorDetalladoResponse(SensorResponse):
    """Respuesta con información detallada del sensor"""
    total_lecturas: int = 0
    ultima_lectura: Optional[datetime] = None
    estado_salud: Optional[str] = None
    
    class Config:
        from_attributes = True


class SensorListResponse(BaseModel):
    """Respuesta para lista de sensores"""
    sensores: List[SensorResponse]
    total: int
    pagina: int
    por_pagina: int


# ========== QUERY PARAMS ==========

class SensorQueryParams(BaseModel):
    """Parámetros de query para filtrado de sensores"""
    planta_id: Optional[UUID] = None
    tipo: Optional[TipoSensorEnum] = None
    activo: Optional[bool] = None
    nombre_contiene: Optional[str] = None
    pagina: int = Field(1, ge=1, description="Número de página")
    por_pagina: int = Field(10, ge=1, le=100, description="Elementos por página")
    
    class Config:
        extra = "forbid"  # No permitir campos extra