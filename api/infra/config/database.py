# infraestructura/configuracion/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .settings import settings
from contextlib import contextmanager
from typing import Generator
import logging
from .settings import settings

#CONEXION Y SESIONES DE BASE DE DATOS

logger = logging.getLogger(__name__)

# Base para modelos ORM
Base = declarative_base()

# Engine de SQLAlchemy
engine = create_engine(settings.DATABASE_URL, echo=True)  # Verifica conexiones antes de usarlas

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

#def init_db() -> None:    ->> NO, MEJOR USAR ALEMBIC  -> alembic init alembic


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para FastAPI
    Proporciona una sesión de base de datos y la cierra automáticamente
    
    Uso en endpoints:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db         # fastapi inyecta desde endpoints
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager para usar fuera de FastAPI
    
    Uso:
        with get_db_context() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def dispose_db() -> None:
    """Cierra todas las conexiones del pool"""
    engine.dispose()
    logger.info("Conexiones de base de datos cerradas")


# Event listener para SQLite (si lo usas en desarrollo)  NO ES EL CASO
#@event.listens_for(Engine, "connect")
#def set_sqlite_pragma(dbapi_conn, connection_record):
#    """Habilita foreign keys en SQLite"""
