from uuid import UUID
from application.ports.repositories import PlantaRepository
from domain.entities.planta import Planta # Asegúrate de tener tu entidad de dominio

class PlantaService:
    def __init__(self, planta_repo: PlantaRepository):
        self.planta_repo = planta_repo

    async def crear_planta(self, nombre: str, ubicacion: str) -> Planta:
        # Aquí crearías la entidad de dominio
        nueva_planta = Planta(nombre=nombre, ubicacion=ubicacion)
        # Y la guardas a través del repositorio
        return await self.planta_repo.guardar(nueva_planta)

    async def obtener_todas(self):
        return await self.planta_repo.obtener_todos()

    async def obtener_por_id(self, planta_id: UUID):
        return await self.planta_repo.obtener_por_id(planta_id)
    
    async def obtener_sensores_de_planta(self, planta_id: UUID):
        # Este método coordina con el repositorio de sensores
        return await self.planta_repo.obtener_todos(planta_id)