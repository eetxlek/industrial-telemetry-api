"""
Exportar todos los schemas
"""
from .sensor import (
    SensorCreateRequest,
    SensorUpdateRequest,
    SensorEstadoRequest,
    SensorResponse,
    SensorDetalladoResponse,
    SensorListResponse,
    SensorQueryParams,
    TipoSensorEnum
)

from .telemetria import (
    TelemetriaCreateRequest,
    TelemetriaLoteRequest,
    TelemetriaResponse,
    TelemetriaSimpleResponse,
    TelemetriaListResponse,
    TelemetriaQueryParams
)

from .metrica import (
    MetricaResponse,
    MetricaTendenciaResponse,
    MetricaComparativaResponse,
    MetricaQueryParams
)

from .requests import (
    PaginacionRequest,
    FiltroTemporalRequest,
    FiltroValorRequest,
    BusquedaRequest,
    AlertaConfigRequest,
    ExportacionRequest,
    IntegridadRequest,
    BatchRequest
)

__all__ = [
    # Sensor
    "SensorCreateRequest",
    "SensorUpdateRequest",
    "SensorEstadoRequest",
    "SensorResponse",
    "SensorDetalladoResponse",
    "SensorListResponse",
    "SensorQueryParams",
    "TipoSensorEnum",
    
    # Telemetría
    "TelemetriaCreateRequest",
    "TelemetriaLoteRequest",
    "TelemetriaResponse",
    "TelemetriaSimpleResponse",
    "TelemetriaListResponse",
    "TelemetriaQueryParams",
    
    # Métricas
    "MetricaResponse",
    "MetricaTendenciaResponse",
    "MetricaComparativaResponse",
    "MetricaQueryParams",
    
    # Requests comunes
    "PaginacionRequest",
    "FiltroTemporalRequest",
    "FiltroValorRequest",
    "BusquedaRequest",
    "AlertaConfigRequest",
    "ExportacionRequest",
    "IntegridadRequest",
    "BatchRequest"
]