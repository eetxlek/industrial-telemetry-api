"""
Endpoints REST para sensores
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from api.infra.adapters.rest.schemas.sensor import SensorCreateRequest, SensorResponse
from application.services.sensor_service import SensorService
from infra.config.inyeccion_dependencias import get_sensor_service

router = APIRouter(prefix="/sensores", tags=["sensores"])

#Crear sensor
@router.post(
    "/",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo sensor",
    description="Crea un nuevo sensor en una planta específica"
)
async def crear_sensor(
    request: SensorCreateRequest,
    service: SensorService = Depends(get_sensor_service)
):
    try:
        sensor = await service.crear_sensor(
            planta_id=request.planta_id,
            nombre=request.nombre,
            tipo=request.tipo,
            unidad=request.unidad
        )
        return SensorResponse.from_entity(sensor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

#activar
@router.post(
    "/{sensor_id}/activar",
    summary="Activar sensor",
    description="Activa un sensor que estaba desactivado"
)
async def activar_sensor(
    sensor_id: UUID,
    service: SensorService = Depends(get_sensor_service)
):
    success = await service.activar_sensor(sensor_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Sensor {sensor_id} no encontrado"
        )
    
    return {"message": "Sensor activado exitosamente"}

#desactivar
@router.post(
    "/{sensor_id}/desactivar",
    summary="Desactivar sensor",
    description="Desactiva un sensor activo"
)
async def desactivar_sensor(
    sensor_id: UUID,
    service: SensorService = Depends(get_sensor_service)
):
    success = await service.desactivar_sensor(sensor_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudo desactivar el sensor. Verifique que no tenga lecturas recientes."
        )
    
    return {"message": "Sensor desactivado exitosamente"}


