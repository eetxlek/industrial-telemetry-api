from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

from domain.entities.planta import Planta

class PlantaCreateRequest(BaseModel):
    nombre: str
    ubicacion: Optional[str] = "No especificada"

class PlantaResponse(BaseModel):
    id: UUID
    nombre: str
    ubicacion: str
    activa: bool
    fecha_creacion: datetime

    model_config = {
        "from_attributes": True  # Versión Pydantic v2 en vez de Class config: orm_mode =true
    }

    @classmethod
    def from_entity(cls, entity:Planta):
        return cls(
            id=entity.id,
            nombre=entity.nombre,
            ubicacion=entity.ubicacion,
            activa=entity.activa,
            fecha_creacion=entity.fecha_creacion
        )
