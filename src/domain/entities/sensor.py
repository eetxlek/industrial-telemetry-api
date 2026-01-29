"""
Entidad Sensor - Dominio puro
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from enum import Enum

from domain.value_objects.metrica import Metrica
from domain.entities.telemetria import Telemetria


class TipoSensor(str, Enum):
    """Tipos de sensores disponibles"""
    TEMPERATURA = "temperatura"       # Mide la energía térmica del ambiente o superficies. Esencial para control climático y procesos industriales. # Sensor termoeléctrico que mide grados Celsius/Kelvin. Usado en HVAC, procesos químicos y electrónica.
    PRESION = "presion"               # Detecta fuerza por unidad de área en fluidos o gases. Crítico para sistemas neumáticos y de fluidos. # Transductor que convierte fuerza en señal eléctrica. Aplicado en bombas, compresores y sistemas hidráulicos.
    HUMEDAD = "humedad"               # Cuantifica la cantidad de vapor de agua en el aire o material. Fundamental para agricultura y conservación. # Sensor capacitivo o resistivo que mide humedad relativa. Esencial en invernaderos y almacenamiento.
    VIBRACION = "vibracion"           # Registra oscilaciones mecánicas en estructuras. Vital para mantenimiento predictivo de maquinaria. # Acelerómetro que detecta frecuencias y amplitudes. Para monitoreo de rodamientos y estructuras.
    CAUDAL = "caudal"                 # Mide el volumen de fluido que pasa por punto en tiempo. Clave para gestión de recursos hídricos. # Sensor magnético o ultrasónico que mide flujo volumétrico. Util en tratamiento de agua y petróleo.

#Entidad
@dataclass
class Sensor:
    """Representa un sensor en una planta"""
    id: UUID
    planta_id: UUID
    nombre: str
    tipo: TipoSensor
    unidad: str
    activo: bool = True

     # ✅ OBJETOS RELACIONADOS (encapsulados)
    _telemetrias: List[Telemetria] = field(default_factory=list)
    _ultimo_hash: str = "0"  # Hash del último registro (para encadenamiento)

    #Factory method para patron de creación
    @staticmethod
    def crear(planta_id: UUID, nombre: str, tipo: TipoSensor, unidad: str) -> 'Sensor':
        """Factory method para crear un nuevo sensor con estado inicial valido"""
        return Sensor(
            id=uuid4(),
            planta_id=planta_id,
            nombre=nombre,
            tipo=tipo,
            unidad=unidad,
            activo=True,
            _telemetrias=[],
            _ultimo_hash="0"

        )
    #Comportamiento de dominio

    # ✅ COMPORTAMIENTO DE DOMINIO PRINCIPAL
    def registrar_lectura(self, valor: float, timestamp: Optional[datetime] = None) -> Telemetria:
        """
        Regla de negocio: registrar nueva telemetría con integridad garantizada
        """
        if not self.activo:
            raise ValueError(f"Sensor {self.nombre} ({self.id}) está desactivado")
        
        # Validar valor según tipo de sensor
        self._validar_valor(valor)
        
        # Usar timestamp actual si no se proporciona
        timestamp = timestamp or datetime.utcnow()
        
        # Crear nueva telemetría encadenada
        telemetria = Telemetria.crear(
            sensor_id=self.id,
            valor=valor,
            timestamp=timestamp,
            previous_hash=self._ultimo_hash  # Encadenamiento
        )
        
        # Agregar a la colección
        self._telemetrias.append(telemetria)
        
        # Actualizar hash para próxima telemetría
        self._ultimo_hash = telemetria.payload_hash
        
        return telemetria
    
    def _validar_valor(self, valor: float) -> None:
        """Reglas de validación específicas por tipo de sensor"""
        if self.tipo == TipoSensor.TEMPERATURA and valor < -273.15:
            raise ValueError("Temperatura no puede ser menor al cero absoluto (-273.15°C)")
        elif self.tipo == TipoSensor.HUMEDAD and (valor < 0 or valor > 100):
            raise ValueError("Humedad relativa debe estar entre 0% y 100%")
        elif self.tipo == TipoSensor.PRESION and valor < 0:
            raise ValueError("Presión no puede ser negativa")
        elif self.tipo == TipoSensor.VIBRACION and valor < 0:
            raise ValueError("Nivel de vibración no puede ser negativo")
        elif self.tipo == TipoSensor.CAUDAL and valor < 0:
            raise ValueError("Caudal no puede ser negativo")
        
    # ✅ MÉTODOS DE CONSULTA (devuelven Value Objects o copias)
    def obtener_metricas(self, desde: Optional[datetime] = None, 
                        hasta: Optional[datetime] = None) -> 'Metrica':
        """
        Calcula métricas para un período específico
        Devuelve un Value Object inmutabl
        """
        # Filtrar telemetrías por período
        telemetrias_filtradas = self._filtrar_por_periodo(desde, hasta)
        
        if not telemetrias_filtradas:
            raise ValueError(f"No hay telemetrías en el período especificado para sensor {self.nombre}")
        
        valores = [t.valor for t in telemetrias_filtradas]
        
        return Metrica(
            sensor_id=self.id,
            sensor_nombre=self.nombre,
            valor_promedio=sum(valores) / len(valores),
            valor_minimo=min(valores),
            valor_maximo=max(valores),
            total_registros=len(valores),
            unidad=self.unidad,
            periodo_inicio=desde,
            periodo_fin=hasta
        )
    
    def _filtrar_por_periodo(self, desde: Optional[datetime], 
                            hasta: Optional[datetime]) -> List[Telemetria]:
        """Filtra telemetrías por rango de tiempo"""
        filtradas = self._telemetrias
        
        if desde:
            filtradas = [t for t in filtradas if t.timestamp >= desde]
        if hasta:
            filtradas = [t for t in filtradas if t.timestamp <= hasta]
        
        return filtradas
    
    def verificar_integridad_cadena(self) -> Tuple[bool, List[str]]:
        """
        Verifica la integridad de toda la cadena de telemetrías
        Devuelve (es_válida, lista_de_errores)
        """
        errores = []
        
        for i, telemetria in enumerate(self._telemetrias):
            # Verificar hash individual
            if not telemetria.verificar_integridad():
                errores.append(f"Telemetría {i} (id={telemetria.id}): hash inválido")
            
            # Verificar encadenamiento (excepto la primera)
            if i > 0:
                if telemetria.previous_hash != self._telemetrias[i-1].payload_hash:
                    errores.append(f"Telemetría {i}: encadenamiento roto")
        
        return (len(errores) == 0, errores)

    # ✅ COMPORTAMIENTO DE GESTIÓN
    def desactivar(self) -> None:
        """
        Regla de negocio: condiciones para desactivar sensor
        """
        if self._telemetrias:
            ultima_lectura = self._telemetrias[-1].timestamp
            horas_desde_ultima = (datetime.utcnow() - ultima_lectura).total_seconds() / 3600
            
            if horas_desde_ultima < 24:
                raise ValueError(
                    f"No se puede desactivar sensor con lecturas en las últimas 24 horas "
                    f"(última: {ultima_lectura})"
                )
        
        self.activo = False
    
    def activar(self) -> None:
        """Activa el sensor"""
        self.activo = True

    def eliminar_telemetrias_anteriores(self, fecha_limite: datetime) -> int:
        """
        Elimina telemetrías anteriores a fecha_limite
        Devuelve cantidad eliminada
        """
        original_count = len(self._telemetrias)
        
        # Mantener solo las telemetrías recientes
        self._telemetrias = [
            t for t in self._telemetrias 
            if t.timestamp >= fecha_limite
        ]
        
        eliminadas = original_count - len(self._telemetrias)
        
        # Si se eliminaron, actualizar encadenamiento
        if eliminadas > 0 and self._telemetrias:
            self._reconstruir_cadena_desde_indice(0)
        
        return eliminadas
    
    def _reconstruir_cadena_desde_indice(self, indice_inicio: int) -> None:
        """Reconstruye la cadena de hashes desde un índice específico"""
        if indice_inicio >= len(self._telemetrias):
            return
        
        # Primer elemento usa hash "0" o del elemento anterior si existe
        previous_hash = "0" if indice_inicio == 0 else self._telemetrias[indice_inicio-1].payload_hash
        
        for i in range(indice_inicio, len(self._telemetrias)):
            telemetria = self._telemetrias[i]
            
            # Recalcular con nuevo previous_hash
            nueva_telemetria = Telemetria.crear(
                sensor_id=telemetria.sensor_id,
                valor=telemetria.valor,
                timestamp=telemetria.timestamp,
                previous_hash=previous_hash
            )
            
            # Reemplazar manteniendo el ID original
            self._telemetrias[i] = Telemetria(
                id=telemetria.id,  # Mantener ID original
                sensor_id=nueva_telemetria.sensor_id,
                valor=nueva_telemetria.valor,
                timestamp=nueva_telemetria.timestamp,
                payload_hash=nueva_telemetria.payload_hash,
                previous_hash=nueva_telemetria.previous_hash
            )
            
            previous_hash = nueva_telemetria.payload_hash
        
        # Actualizar último hash del agregado
        if self._telemetrias:
            self._ultimo_hash = self._telemetrias[-1].payload_hash

        # ✅ PROPIEDADES PARA ACCESO CONTROLADO
    @property
    def total_lecturas(self) -> int:
        return len(self._telemetrias)
    
    @property
    def ultima_lectura(self) -> Optional[Telemetria]:
        return self._telemetrias[-1] if self._telemetrias else None
    
    
    def lecturas_recientes(self, n: int = 10) -> List[Telemetria]:
        """Devuelve copia de las últimas n lecturas"""
        if n <= 0:
            raise ValueError("n debe ser mayor a 0")
        return self._telemetrias[-n:] if self._telemetrias else []
    
    @property
    def cadena_valida(self) -> bool:
        """Verifica rápidamente si la cadena es válida"""
        valida, _ = self.verificar_integridad_cadena()
        return valida