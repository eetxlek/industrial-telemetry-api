"""
Servicio de auditoría para verificar integridad de cadenas de telemetría
"""
from typing import List, Tuple
from uuid import UUID
from application.ports.repositories import TelemetriaRepository

#audita integirdad de datos. Si la cadena se manipula, elimina o inserta, deja huella. 
class AuditoriaService:
    """Verifica integridad blockchain-like de cadenas de telemetría"""
    
    def __init__(self, telemetria_repo: TelemetriaRepository):
        """
        Args:
            telemetria_repo: Repositorio para acceder a telemetrías
        """
        self.telemetria_repo = telemetria_repo
    
    async def ejecutar_auditoria(
        self, 
        sensor_id: UUID,
        limite: int = 100
    ) -> Tuple[bool, str]:
        """
        Verifica la integridad de la cadena de hashes de un sensor
        
        Args:
            sensor_id: ID del sensor a auditar
            limite: Número máximo de telemetrías a verificar (últimas N)
        
        Returns:
            (es_valido, mensaje):
                - es_valido: True si la cadena es íntegra
                - mensaje: Descripción del resultado o error encontrado
        
        Ejemplo:
            >>> es_valido, msg = await service.ejecutar_auditoria(sensor_id)
            >>> if not es_valido:
            >>>     logger.error(f"Integridad comprometida: {msg}")
        """
        # Obtener telemetrías en orden cronológico
        historial = await self.telemetria_repo.obtener_por_sensor(
            sensor_id=sensor_id,
            limite=limite,
            orden="ASC"  # Cronológico para verificar encadenamiento
        )
        
        # Caso: sensor sin telemetrías
        if not historial:
            return True, "Sensor sin telemetrías (cadena vacía es válida)"
        
        # Verificar cada telemetría
        for i, registro in enumerate(historial):
            # 1. Verificar integridad del hash propio
            if not registro.verificar_integridad():
                return False, (
                    f"Corrupción detectada en registro {i}: "
                    f"ID={registro.id}, "
                    f"hash inválido"
                )
            
            # 2. Verificar encadenamiento con anterior
            if i > 0:
                hash_esperado = historial[i-1].payload_hash
                if registro.previous_hash != hash_esperado:
                    return False, (
                        f"Cadena rota en registro {i}: "
                        f"ID={registro.id}, "
                        f"esperado previous_hash={hash_esperado}, "
                        f"encontrado={registro.previous_hash}"
                    )
        
        # Éxito: toda la cadena es válida
        return True, (
            f"Cadena íntegra: {len(historial)} telemetrías verificadas "
            f"(últimas {limite} registros)"
        )
    
    async def verificar_sensores_lote(
        self, 
        sensor_ids: List[UUID],
        limite_por_sensor: int = 100
    ) -> List[dict]:
        """
        Ejecuta auditoría en múltiples sensores
        
        Args:
            sensor_ids: Lista de IDs de sensores a auditar
            limite_por_sensor: Telemetrías a verificar por sensor
        
        Returns:
            Lista de reportes con formato:
            [
                {
                    "sensor_id": UUID,
                    "valido": bool,
                    "detalle": str
                },
                ...
            ]
        
        Ejemplo:
            >>> reportes = await service.verificar_sensores_lote([id1, id2])
            >>> sensores_corruptos = [r for r in reportes if not r["valido"]]
        """
        resultados = []
        
        for sensor_id in sensor_ids:
            es_valido, mensaje = await self.ejecutar_auditoria(
                sensor_id, 
                limite=limite_por_sensor
            )
            
            resultados.append({
                "sensor_id": str(sensor_id),  # Serializable para JSON
                "valido": es_valido,
                "detalle": mensaje
            })
        
        return resultados