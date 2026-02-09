"""
Schemas de request comunes para la API
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PaginacionRequest(BaseModel):
    """Request base con paginación"""
    pagina: int = Field(1, ge=1, description="Número de página")
    por_pagina: int = Field(10, ge=1, le=100, description="Elementos por página")


class FiltroTemporalRequest(BaseModel):
    """Request base con filtro temporal"""
    desde: Optional[datetime] = Field(
        None,
        description="Fecha de inicio (inclusive)"
    )
    hasta: Optional[datetime] = Field(
        None,
        description="Fecha de fin (inclusive)"
    )
    
    @field_validator('hasta')
    def validar_rango_fechas(cls, v, values):
        if 'desde' in values and values['desde'] and v:
            if v < values['desde']:
                raise ValueError('La fecha "hasta" debe ser mayor o igual a "desde"')
        return v


class FiltroValorRequest(BaseModel):
    """Request base con filtro por valor"""
    valor_min: Optional[float] = Field(
        None,
        description="Valor mínimo"
    )
    valor_max: Optional[float] = Field(
        None,
        description="Valor máximo"
    )
    
    @field_validator('valor_max')
    def validar_rango_valores(cls, v, values):
        if 'valor_min' in values and values['valor_min'] is not None and v is not None:
            if v < values['valor_min']:
                raise ValueError('El valor máximo debe ser mayor o igual al mínimo')
        return v


class BusquedaRequest(BaseModel):
    """Request base con búsqueda"""
    query: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Texto de búsqueda"
    )


# ========== REQUESTS ESPECÍFICAS ==========

class AlertaConfigRequest(BaseModel):
    """Request para configurar alertas de sensor"""
    sensor_id: UUID
    umbral_desviacion: Optional[float] = Field(
        None,
        ge=1.0,
        le=5.0,
        description="Umbral de desviaciones estándar para outlier"
    )
    ventana_temporal_horas: Optional[int] = Field(
        None,
        ge=1,
        le=168,
        description="Ventana temporal en horas para análisis"
    )
    min_lecturas_para_analisis: Optional[int] = Field(
        None,
        ge=5,
        le=1000,
        description="Mínimo de lecturas para análisis estadístico"
    )
    rango_min: Optional[float] = Field(
        None,
        description="Valor mínimo del rango esperado"
    )
    rango_max: Optional[float] = Field(
        None,
        description="Valor máximo del rango esperado"
    )
    
    @field_validator('rango_max')
    def validar_rango(cls, v, values):
        if 'rango_min' in values and values['rango_min'] is not None and v is not None:
            if v <= values['rango_min']:
                raise ValueError('El valor máximo debe ser mayor al mínimo')
        return v


class ExportacionRequest(FiltroTemporalRequest):
    """Request para exportación de datos"""
    formato: str = Field("json", description="Formato de exportación")
    incluir_telemetrias: bool = Field(
        True,
        description="Incluir telemetrías en la exportación"
    )
    limite: Optional[int] = Field(
        None,
        ge=1,
        le=10000,
        description="Límite de registros a exportar"
    )
    
    @field_validator('formato')
    def formato_valido(cls, v):
        if v not in ['json', 'csv']:
            raise ValueError('Formato debe ser json o csv')
        return v


class IntegridadRequest(BaseModel):
    """Request para verificación de integridad"""
    sensor_id: UUID
    profundidad: Optional[int] = Field(
        1000,
        ge=1,
        le=10000,
        description="Número máximo de telemetrías a verificar"
    )
    reparar: bool = Field(
        False,
        description="Intentar reparar la cadena si se encuentra corrompida"
    )


class BatchRequest(BaseModel):
    """Request para operaciones en lote"""
    operacion: str = Field(
        ...,
        description="Tipo de operación (activar, desactivar, eliminar, exportar)"
    )
    sensor_ids: List[UUID] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="IDs de los sensores a procesar"
    )
    parametros: Optional[dict] = Field(
        None,
        description="Parámetros adicionales para la operación"
    )
    
    @field_validator('operacion')
    def operacion_valida(cls, v):
        operaciones_validas = ['activar', 'desactivar', 'eliminar', 'exportar']
        if v not in operaciones_validas:
            raise ValueError(f'Operación debe ser una de: {operaciones_validas}')
        return v