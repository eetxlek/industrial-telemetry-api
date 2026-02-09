"""
Exportar routers de endpoints
"""
from .sensores import router as sensores_router
from .telemetria import router as telemetria_router
from .metricas import router as metricas_router

__all__ = [
    "sensores_router",
    "telemetria_router", 
    "metricas_router"
]