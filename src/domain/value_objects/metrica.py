"""
Value Object Metrica - Dominio puro
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

#inmutable, value object. Se comparan por sus atributos, no por su identidad unica como en agregados. Aqui dos metricas con valores iguales, son iguales. Solo almacena datos.
@dataclass(frozen=True)
class Metrica:
    """
    Value object que representa métricas agregadas de telemetría
    Inmutable para garantizar integridad
    """
    sensor_id: UUID
    sensor_nombre: str
    valor_promedio: float
    valor_minimo: float
    valor_maximo: float
    total_registros: int
    unidad: str
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de integridad"""
        if self.total_registros < 0:
            raise ValueError("total_registros no puede ser negativo")
        if self.valor_minimo > self.valor_maximo:
            raise ValueError("valor_minimo no puede ser mayor que valor_maximo")
        
    # devuelve mettrica estadística calculada a partir de value object metrica.
    @property
    def rango(self) -> float:
        """Rango entre máximo y mínimo, amplitud total entre mediciones"""
        return self.valor_maximo - self.valor_minimo
    
    @property
    def variabilidad_relativa(self) -> float:
        """Coeficiente de variación (si hay registros), variabilidad en relación a su media. Estabilidad del sensor"""
        if self.valor_promedio == 0 or self.total_registros == 0:
            return 0.0
        return (self.rango / self.valor_promedio) * 100