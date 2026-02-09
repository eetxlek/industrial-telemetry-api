"""
Schemas Pydantic para Métricas
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ========== RESPONSE SCHEMAS ==========

class MetricaBaseResponse(BaseModel):
    """Base para respuestas de métricas"""
    sensor_id: UUID
    sensor_nombre: str
    valor_promedio: float
    valor_minimo: float
    valor_maximo: float
    total_registros: int
    unidad: str


class MetricaResponse(MetricaBaseResponse):
    """Respuesta de métricas"""
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    rango: float
    variabilidad_relativa: float
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_value_object(cls, metrica) -> 'MetricaResponse':
        """Crea response desde value object de dominio"""
        return cls(
            sensor_id=metrica.sensor_id,
            sensor_nombre=metrica.sensor_nombre,
            valor_promedio=metrica.valor_promedio,
            valor_minimo=metrica.valor_minimo,
            valor_maximo=metrica.valor_maximo,
            total_registros=metrica.total_registros,
            unidad=metrica.unidad,
            periodo_inicio=metrica.periodo_inicio,
            periodo_fin=metrica.periodo_fin,
            rango=metrica.rango,
            variabilidad_relativa=metrica.variabilidad_relativa
        )


class MetricaTendenciaResponse(BaseModel):
    """Respuesta de tendencias de métricas"""
    sensor_id: UUID
    periodo: str
    valores_promedio: list = Field(..., description="Valores promedio por intervalo")
    timestamps: list = Field(..., description="Timestamps de los intervalos")
    tendencia: str = Field(..., description="Dirección de la tendencia")
    cambio_porcentual: float


class MetricaComparativaResponse(BaseModel):
    """Respuesta de comparación de métricas entre sensores"""
    periodo: str
    sensores: list = Field(
        ...,
        description="Lista de métricas por sensor en el período"
    )
    mejor_sensor: Optional[dict] = Field(
        None,
        description="Sensor con mejor rendimiento"
    )
    peor_sensor: Optional[dict] = Field(
        None,
        description="Sensor con peor rendimiento"
    )


# ========== QUERY PARAMS ==========

class MetricaQueryParams(BaseModel):
    """Parámetros de query para cálculo de métricas"""
    sensor_id: UUID = Field(..., description="ID del sensor")
    desde: Optional[datetime] = Field(
        None,
        description="Fecha de inicio del período"
    )
    hasta: Optional[datetime] = Field(
        None,
        description="Fecha de fin del período"
    )
    intervalo: Optional[str] = Field(
        None,
        description="Intervalo para agrupación (hour, day, week, month)"
    )
    
    @field_validator('intervalo')
    def intervalo_valido(cls, v):
        if v is not None and v not in ['hour', 'day', 'week', 'month']:
            raise ValueError('Intervalo debe ser: hour, day, week o month')
        return v
    
    @field_validator('hasta')
    def validar_rango_fechas(cls, v, values):
        if 'desde' in values and values['desde'] and v:
            if v < values['desde']:
                raise ValueError('La fecha "hasta" debe ser mayor o igual a "desde"')
        return v