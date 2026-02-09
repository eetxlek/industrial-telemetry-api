# infraestructura/configuracion/logging_config.py

import logging
import sys
from pythonjsonlogger import jsonlogger
from .settings import settings

#CONFIGURACION D ELOGS
def setup_logging():
    """
    Configura el sistema de logging de la aplicación
    """
    
    # Nivel de log
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Crear handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Formato según configuración
    if settings.LOG_FORMAT == "json":
        # Formato JSON para producción (mejor para parsear)
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Formato texto para desarrollo (más legible)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Silenciar logs verbosos de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logging.info(f"Logging configurado - Nivel: {settings.LOG_LEVEL}, Formato: {settings.LOG_FORMAT}")