
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from pathlib import Path
import os

#VARIABLES DE ENTORNO Y CONFIGURACION
def _load_env_if_needed():
    """
    Carga .env solo si no estamos en un entorno con variables ya definidas
    (Docker, CI/CD, etc.)
    """
    if os.getenv("DATABASE_URL") is not None:   # garantiza que gargue .env aunque url no esté definida
        return
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    ENV_FILE = BASE_DIR / ".env"
    
    if ENV_FILE.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=ENV_FILE, override=False)


# Cargar .env antes de instanciar Settings
_load_env_if_needed()


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación
    Lee variables de entorno y archivo .env
    """
    
    # ==========================================
    # APLICACIÓN
    # ==========================================
    APP_NAME: str = "Telemetria API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ==========================================
    # API
    # ==========================================
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - separado por comas en .env
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def origins_list(self) -> List[str]:
        """Convierte string de origins separados por coma a lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
    
    # Rate Limiting (slowapi)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ==========================================
    # BASE DE DATOS
    # ==========================================
    DATABASE_URL: str  # Requerido, sin default
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True  # Verifica conexiones antes de usar
    
    # ==========================================
    # SEGURIDAD
    # ==========================================
    SECRET_KEY: str  # Requerido, sin default
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==========================================
    # LOGGING
    # ==========================================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "text"  # text o json
    
    # ==========================================
    # CONFIGURACIÓN DE PYDANTIC
    # ==========================================
    model_config = {
        "case_sensitive": True,
        "extra": "ignore"  # Ignora variables extra en .env
    }
    
    # ==========================================
    # VALIDACIÓN PERSONALIZADA
    # ==========================================
    def validate_environment(self) -> None:
        """Validaciones adicionales de configuración"""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "change-this-in-production":
                raise ValueError("SECRET_KEY debe cambiarse en producción")
            if self.DEBUG:
                raise ValueError("DEBUG debe ser False en producción")
            if self.DATABASE_ECHO:
                raise ValueError("DATABASE_ECHO debe ser False en producción")


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton para obtener configuración
    Se cachea para no leer el .env múltiples veces
    """
    settings = Settings()
    #settings.validate_environment()
    return settings


# Instancia global para importar fácilmente
settings = get_settings()