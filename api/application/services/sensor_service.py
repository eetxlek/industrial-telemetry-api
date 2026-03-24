from typing import List
from uuid import UUID
from api.application.ports.event_publisher import EventPublisher
from api.application.ports.repositories import SensorRepository, TelemetriaRepository
from api.domain.entities.sensor import Sensor, TipoSensor
from api.domain.value_objects.metrica import Metrica

# Gestion de la infra del aparato: crea, update,delete, obtener,listar,activar,desactivar
class SensorService:
    def __init__(
        self,
        sensor_repo: SensorRepository,
        telemetria_repo: TelemetriaRepository,
        event_publisher: EventPublisher  # publica eventos de dominio
    ):
        self.sensor_repo = sensor_repo
        self.telemetria_repo = telemetria_repo
        self.event_publisher = event_publisher


    # Crear sensor ✅
    async def crear_sensor(self, planta_id: UUID, nombre: str, tipo: TipoSensor, unidad: str) -> Sensor:
        sensor = Sensor.crear(planta_id, nombre, tipo, unidad)
        await self.sensor_repo.guardar(sensor)

        # Publicar evento
        event = sensor.to_creado_event()
        await self.event_publisher.publicar(event)

        return sensor

    async def obtener_metricas_planta(self, planta_id: str) -> List[Metrica]:
        # 1. Obtener los sensores de la planta
        sensores = await self.sensor_repo.obtener_por_planta(planta_id)

        resultados = []
        for sensor in sensores:
        # 2. Obtener las telemetrías/métricas actuales para esos sensores
            teles= await self.telemetria_repo.obtener_por_sensor(sensor.id, limite=1)
            if teles:
                # 3. Mapeamos a tu Value Object Metrica, "magia estadistica"
                valores = [t.valor for t in teles]
            
                metrica_vo = Metrica(
                    sensor_id=sensor.id,
                    sensor_nombre=sensor.nombre,
                    valor_promedio=sum(valores) / len(valores),
                    valor_minimo=min(valores),
                    valor_maximo=max(valores),
                    total_registros=len(teles),
                    unidad="Celsius", # O sacarlo del sensor.tipo
                    periodo_inicio=teles[-1].timestamp,
                    periodo_fin=teles[0].timestamp
                )
                resultados.append(metrica_vo)
        return resultados

    # Activar sensor ✅
    async def activar_sensor(self, sensor_id: UUID) -> Sensor:
        sensor = await self.sensor_repo.obtener_por_id(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} no encontrado")
        sensor.activar()
        event = sensor.to_estado_cambiado_event(motivo="Activación manual")
        await self.sensor_repo.guardar(sensor)
        await self.event_publisher.publicar(event)
        return sensor

    # Desactivar sensor ✅
    async def desactivar_sensor(self, sensor_id: UUID) -> Sensor:
        sensor = await self.sensor_repo.obtener_por_id(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} no encontrado")
        sensor.desactivar()
        await self.sensor_repo.guardar(sensor)
        event = sensor.to_estado_cambiado_event(motivo="Desactivación manual")
        await self.event_publisher.publicar(event)
        return sensor

    # Eliminar sensor (opcional) ✅
    async def eliminar_sensor(self, sensor_id: UUID) -> bool:
        return await self.sensor_repo.eliminar(sensor_id)
