from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID
from api.application.ports.event_publisher import EventPublisher
from api.application.ports.repositories import SensorRepository, TelemetriaRepository
from api.domain.entities.telemetria import Telemetria
from api.domain.events.telemetria_events import TelemetriaRegistrada
from sqlalchemy.ext.asyncio import AsyncSession

# Resgistrar lectura con hash, registrar lote, obtener lecturas, ultima lectura (get historicos))
class TelemetriaService:
    def __init__(
        self,
        sensor_repo: SensorRepository,
        telemetria_repo: TelemetriaRepository,
        event_publisher: EventPublisher,
        session: AsyncSession
    ):
        self.sensor_repo = sensor_repo
        self.telemetria_repo = telemetria_repo
        self.event_publisher = event_publisher
        self.session = session

    # Registrar lectura ✅
    async def registrar_lectura(self, sensor_id: UUID, valor: float) -> Telemetria:
        #1.Valida, obtiene datos
        sensor = await self.sensor_repo.obtener_por_id(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} no encontrado")
        # 2. Validar con lógica de dominio del Sensor
        if not sensor.puede_registrar_lectura():
            raise ValueError(f"Sensor {sensor_id} está desactivado")
        sensor.validar_valor(valor) 
        #obtener ultimo hash de bd (fuente verdad)
        ultimo_hash = await self.telemetria_repo.obtener_ultimo_hash(sensor_id) or "0"
        #crea entidad dominio
        telemetria = Telemetria.crear(
            sensor_id=sensor_id,
            valor=valor,
            timestamp=datetime.now(timezone.utc),
            previous_hash=ultimo_hash
        )
        # Prepara la persistencia, stage
        await self.telemetria_repo.guardar(telemetria)
        
        # Crear evento, como es frozen, asegura pasar todos los campos. event_id y ocurred_at se añaden automatico por el  factory DomainEvent.
        try:
            evento = TelemetriaRegistrada.from_entity(telemetria)

            # Publicar Evento   -----   AQUI SE PUBLICA EN RABBIT pero el dominio aislado de el.
            await self.event_publisher.publicar(evento)

            # SI HA IDO BIEN, grabamos en la DB
            await self.session.commit()
            print("Transacción completada: DB y Evento sincronizados ✅ ")

        except Exception as e:
            # Si falla el evento, hacemos rollback y la DB queda limpia
            await self.session.rollback()
            print(f" Error en el flujo. ❌ Rollback ejecutado: {e}")
            raise e
        
        return telemetria
    
    # aunque no haya guardar lote, como ayncsession vivo, puedes optimiar mas adelante el bulk_save_objects sin tocar endpoint
    async def registrar_lecturas_lote(
        self,
        lecturas: List[Tuple[UUID, float]]
    ) -> List[Telemetria]:

        if not lecturas:
            raise ValueError("No se enviaron lecturas")

        telemetrias_creadas: List[Telemetria] = []
        # Cache de último hash por sensor
        last_hash_por_sensor: dict[UUID, str] = {}
        try: 
            for sensor_id, valor in lecturas:
        
                # 1. Validar sensor
                sensor = await self.sensor_repo.obtener_por_id(sensor_id)
                if not sensor:
                    raise ValueError(f"Sensor {sensor_id} no existe")

                if not sensor.activo:
                    raise ValueError(f"Sensor {sensor_id} está inactivo")
                
                # 2. Obtener último hash correcto
                if sensor_id not in last_hash_por_sensor:
                    last_hash_por_sensor[sensor_id] = (
                        await self.telemetria_repo.obtener_ultimo_hash(sensor_id)
                    )
                previous_hash = last_hash_por_sensor.get(sensor_id, "0")
                # 3. Crear telemetría encadenada
                telemetria = Telemetria.crear(
                    sensor_id=sensor_id,
                    valor=valor,
                    timestamp= datetime.now(timezone.utc),
                    previous_hash=previous_hash
                )
                # 4. persistir
                await self.telemetria_repo.guardar(telemetria)

                # 5. Actualizar hash para la siguiente del mismo sensor
                last_hash_por_sensor[sensor_id] = telemetria.payload_hash

                telemetrias_creadas.append(telemetria)

                # 6. Publicar evento
                evento = TelemetriaRegistrada.from_entity(telemetria)
                await self.event_publisher.publicar(evento)
            # 7. Commit global
            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            raise e
        return telemetrias_creadas


    # Verificar integridad blockchain-like ✅
    async def verificar_integridad(self, sensor_id: UUID) -> dict:
        telemetrias = await self.telemetria_repo.obtener_por_sensor(sensor_id, limite=1000)
        errores = []

        for i, t in enumerate(telemetrias):
            if not t.verificar_integridad():
                errores.append(f"Telemetría {i} hash inválido")
            if i > 0 and t.previous_hash != telemetrias[i-1].payload_hash:
                errores.append(f"Telemetría {i} encadenamiento roto")

        return {
            "sensor_id": str(sensor_id),
            "valido": len(errores) == 0,
            "errores": errores,
            "total_registros": len(telemetrias),
        }

    # Obtener métricas agregadas (promedio, min, max) ✅
    async def obtener_lecturas(
        self,
        sensor_id: UUID,
        limite: int = 100,
        desde=None,
        hasta=None
    ) -> List[Telemetria]:

        return await self.telemetria_repo.obtener_por_sensor(
            sensor_id=sensor_id,
            limite=limite,
            desde=desde,
            hasta=hasta
        )
    
    async def obtener_lecturas_con_info_sensor(self, sensor_id: UUID, limite: int):
        # 1. Obtenemos las lecturas
        telemetrias = await self.telemetria_repo.obtener_por_sensor(
            sensor_id=sensor_id, 
            limite=limite,
            orden="DESC"
        )
        
        # 2. Obtenemos la info del sensor para tener la 'unidad'
        sensor = await self.sensor_repo.obtener_por_id(sensor_id)
        
        return telemetrias, sensor
    
    # Obtener última lectura ✅
    async def obtener_ultima_lectura(self, sensor_id: UUID) -> Optional[Telemetria]:
        return await self.telemetria_repo.obtener_ultima(sensor_id)

    async def obtener_por_id(self, telemetria_id: UUID) -> Telemetria:
        telemetria = await self.telemetria_repo.obtener_por_id(telemetria_id)
        if not telemetria:
            raise ValueError(f"Telemetría {telemetria_id} no encontrada")
        return telemetria
