"""
Puertos para Publicación de Eventos de Dominio - Dominio puro
"""
from abc import ABC, abstractmethod
from typing import Iterable

from domain.events.base import DomainEvent

# ========== PUBLISHER INTERFACE ==========
class EventPublisher(ABC):

    @abstractmethod
    async def publicar(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    async def publicar_lote(self, events: Iterable[DomainEvent]) -> None:
        pass
