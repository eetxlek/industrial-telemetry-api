# test_metadata.py
from pathlib import Path
import sys

# ==========================================
# Agregar src al PYTHONPATH para poder importar infra
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(BASE_DIR))

# ==========================================
# Importar Base y modelos
# ==========================================
from infra.config.database import Base
from infra.events.adapters.persistance.models import *
from infra.config.settings import settings

# ==========================================
# Crear engine de prueba
# ==========================================
from sqlalchemy import create_engine

engine = create_engine(settings.DATABASE_URL)

# ==========================================
# Imprimir tablas detectadas
# ==========================================
print("Tablas detectadas por SQLAlchemy:")
print(list(Base.metadata.tables.keys()))

# ==========================================
# Crear tablas en la base de datos (opcional)
# ==========================================
Base.metadata.create_all(engine)
print("Tablas creadas correctamente en la base de datos.")