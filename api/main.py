# infraestructura/adaptadores/rest/main.py

"""
Punto de entrada de la aplicación FastAPI
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from api.domain.value_objects import metrica
from api.infra.adapters.rest.endpoints import sensores, telemetria
from api.infra.publisher_factory import EventPublisherFactory
from infra.config.settings import settings
from infra.config.database import init_db, dispose_db
from infra.config.logging_config import setup_logging

# Importar routers (ajusta las rutas según tu estructura)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    Ejecuta código al iniciar y al cerrar
    """
    # ==========================================
    # STARTUP
    # ==========================================
    
    # 1. Configurar logging
    setup_logging()
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🌍 Entorno: {settings.ENVIRONMENT}")
    
    # 2. Inicializar base de datos (solo en desarrollo)
    if settings.ENVIRONMENT == "development" and settings.DEBUG:
        logger.info("🔧 Modo desarrollo: inicializando BD automáticamente")
        init_db()
    else:
        logger.warning(
            "⚠️ Producción detectada. Asegúrate de ejecutar: "
            "alembic upgrade head"
        )
    
    # 3. lifespan crea rabit publisher
    event_publisher = EventPublisherFactory.create_publisher()
    await event_publisher.connect()
    #solo una instancia de conexion a rabbit. Evita conexiones innecesarias. 1 conexion por proceso.
    app.state.event_publisher = event_publisher  # solo geteventpublisher(Request) dependency está aware de esto. Fastapi no conoce rabit
    
    logger.info("✅ Aplicación lista y corriendo")
    
    yield  # 🟢 APLICACIÓN CORRIENDO
    
    # ==========================================
    # SHUTDOWN
    # ==========================================
    logger.info("👋 Deteniendo aplicación...")
    
    # 1. Cerrar event publisher
    # if hasattr(app.state, "event_publisher"):
    #     publisher = app.state.event_publisher
    #     if hasattr(publisher, "disconnect"):
    #         await publisher.disconnect()
    
    # 2. Cerrar conexiones de BD
    dispose_db()
    
    logger.info("✅ Aplicación detenida correctamente")


def create_app() -> FastAPI:
    """
    Factory que crea y configura la aplicación FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="API para gestión de sensores y telemetría industrial",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url=f"{settings.API_PREFIX}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_PREFIX}/redoc" if settings.DEBUG else None,
    )
    
    # ==========================================
    # MIDDLEWARE
    # ==========================================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,  # Usa la property que convierte a lista
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ==========================================
    # ROUTERS
    # ==========================================
    app.include_router(
        sensores.router,
        prefix=settings.API_PREFIX,
        tags=["Sensores"]
    )
    app.include_router(
        telemetria.router,
        prefix=settings.API_PREFIX,
        tags=["Telemetría"]
    )
    app.include_router(
        metrica.router,
        prefix=settings.API_PREFIX,
        tags=["Métricas"]
    )
    
    # ==========================================
    # HEALTH CHECK
    # ==========================================
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Endpoint de salud de la aplicación
        """
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        """
        Endpoint raíz - Información básica
        """
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": f"{settings.API_PREFIX}/docs" if settings.DEBUG else "disabled",
            "health": "/health"
        }
    
    return app


# ==========================================
# CREAR APLICACIÓN
# ==========================================
app = create_app()


# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",  # Ajusta según tu estructura
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )