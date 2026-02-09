
# GET /verificar/{sensor_id}

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from application.services.auditoria_service import AuditoriaService
from infra.config.inyeccion_dependencias import get_auditoria_service

router = APIRouter(prefix="/auditoria", tags=["auditorias"])

#INICIALMENTE SIN DEPENDENCIAS DE PLANTA NI BUSCAR EN LISTA DE IDS
@router.get(
    "/sensor/{sensor_id}", 
    summary="Verificar sensor",
    description="Comprueba si las últimas lecturas de un sensor son íntegras"
)
async def verificar_sensor_simple(
    sensor_id: UUID,
    service: AuditoriaService = Depends(get_auditoria_service)
):
    try:
        # Usamos el método que ya tienes escrito y que funciona
        es_valido, mensaje = await service.ejecutar_auditoria(sensor_id)    # -->> da un true o false y contenido
        
        return {
            "sensor_id": sensor_id,
            "integro": es_valido,
            "mensaje": mensaje
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))