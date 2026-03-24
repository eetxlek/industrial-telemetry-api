from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.application.ports.repositories import PlantaRepository
from api.domain.entities.planta import Planta
from api.infra.adapters.persistance.models import PlantaModel

class SQLPlantaRepository(PlantaRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def guardar(self, planta: Planta) -> Planta:
        # Convertimos entidad de dominio a modelo de DB
        modelo = PlantaModel(
            id=planta.id,
            nombre=planta.nombre,
            ubicacion=planta.ubicacion,
            fecha_creacion=planta.fecha_creacion
        )
        self.session.add(modelo)


    async def obtener_por_id(self, id: UUID) -> Optional[Planta]:
        resultado = await self.session.execute(
            select(PlantaModel).where(PlantaModel.id == id)
        )
        modelo = resultado.scalar_one_or_none()
        return modelo.to_entity() if modelo else None # Asumiendo que tu modelo tiene to_entity()

    async def obtener_todos(self) -> List[Planta]:
        resultado = await self.session.execute(select(PlantaModel))
        modelos = resultado.scalars().all()
        return [m.to_entity() for m in modelos]

    def _to_entity(self, modelo: PlantaModel) -> Planta:
        """Convierte modelo a entidad de dominio"""
        return Planta(
            id=modelo.id,
            nombre=modelo.nombre,
            ubicacion=modelo.ubicacion,
            activa=modelo.activa,
            fecha_creacion=modelo.fecha_creacion
        )