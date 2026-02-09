"""
Entidad Planta - Dominio puro
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

@dataclass
class Planta:
    """Representa una planta industrial"""
    id: UUID
    nombre: str
    ubicacion: str
    activa: bool = True
    fecha_creacion: datetime = None    #field(default_factory=datetime.now(timezone.utc))
    
    @staticmethod
    def crear(nombre: str, ubicacion: str) -> 'Planta':
        """Factory method para crear una nueva planta"""
        return Planta(
            id=uuid4(),
            nombre=nombre,
            ubicacion=ubicacion,
            activa=True
        )
    
    def desactivar(self) -> None:
        """Desactiva la planta"""
        self.activa = False
    
    def activar(self) -> None:
        """Activa la planta"""
        self.activa = True