"""
Schemas Pydantic para Telemetría
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from domain.entities.telemetria import Telemetria

# pydantic y DTO

# ========== REQUEST SCHEMAS ==========

class TelemetriaCreateRequest(BaseModel):
    """Schema para crear una telemetría"""
    sensor_id: UUID = Field(..., description="ID del sensor")
    valor: float = Field(..., description="Valor de la lectura")
    timestamp: Optional[datetime] = Field(
        None,
        description="Timestamp de la lectura (UTC por defecto)"
    )
    
    @field_validator('valor')
    def valor_valido(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('El valor debe ser numérico')
        return float(v)


class TelemetriaLoteRequest(BaseModel):
    """Schema para crear múltiples telemetrías en lote"""
    lecturas: List[TelemetriaCreateRequest] = Field(
        ...,
        min_items=1,
        max_items=1000,
        description="Lista de lecturas a registrar"
    )


# ========== RESPONSE SCHEMAS ==========

class TelemetriaBaseResponse(BaseModel):
    """Base para respuestas de telemetría"""
    id: UUID
    sensor_id: UUID
    valor: float
    timestamp: datetime
    payload_hash: str
    previous_hash: str

#detalle completo
class TelemetriaResponse(TelemetriaBaseResponse):
    """Respuesta de telemetría"""
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_entity(cls, telemetria) -> 'TelemetriaResponse':
        """Crea response desde entidad de dominio"""
        return cls(
            id=telemetria.id,
            sensor_id=telemetria.sensor_id,
            valor=telemetria.valor,
            timestamp=telemetria.timestamp,
            payload_hash=telemetria.payload_hash,
            previous_hash=telemetria.previous_hash
        )

#listados
class TelemetriaSimpleResponse(BaseModel):
    """Respuesta simplificada de telemetría (para listados)"""
    id: UUID
    sensor_id: UUID
    valor: float
    timestamp: datetime
    unidad: Optional[str] = None
    
    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, entity: Telemetria, unidad: Optional[str] = None) -> "TelemetriaSimpleResponse":
        """Mapea una entidad de dominio Telemetria a este DTO de respuesta"""
        return cls(
            id=entity.id,
            sensor_id=entity.sensor_id,
            valor=entity.valor,
            timestamp=entity.timestamp,
            unidad=unidad
        )


class TelemetriaListResponse(BaseModel):
    """Respuesta para lista de telemetrías"""
    telemetrias: List[TelemetriaSimpleResponse]
    total: int
    pagina: int
    por_pagina: int
    sensor_nombre: Optional[str] = None
    sensor_unidad: Optional[str] = None


# ========== QUERY PARAMS ==========

class TelemetriaQueryParams(BaseModel):
    """Parámetros de query para filtrado de telemetrías"""
    sensor_id: Optional[UUID] = None
    desde: Optional[datetime] = Field(
        None,
        description="Fecha de inicio (inclusive)"
    )
    hasta: Optional[datetime] = Field(
        None,
        description="Fecha de fin (inclusive)"
    )
    valor_min: Optional[float] = Field(
        None,
        description="Valor mínimo"
    )
    valor_max: Optional[float] = Field(
        None,
        description="Valor máximo"
    )
    pagina: int = Field(1, ge=1)      # control paginacion
    por_pagina: int = Field(50, ge=1, le=1000)
    
    @field_validator('hasta')
    def validar_rango_fechas(cls, v, values):
        if 'desde' in values and values['desde'] and v:
            if v < values['desde']:
                raise ValueError('La fecha "hasta" debe ser mayor o igual a "desde"')
        return v
    
    @field_validator('valor_max')
    def validar_rango_valores(cls, v, values):
        if 'valor_min' in values and values['valor_min'] is not None and v is not None:
            if v < values['valor_min']:
                raise ValueError('El valor máximo debe ser mayor o igual al mínimo')
        return v