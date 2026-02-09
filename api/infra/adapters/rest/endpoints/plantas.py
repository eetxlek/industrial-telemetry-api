from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from api.infra.adapters.rest.schemas.planta import PlantaCreateRequest, PlantaResponse
from application.services.planta_service import PlantaService
from application.services.sensor_service import SensorService
from infra.config.inyeccion_dependencias import get_planta_service, get_sensor_service

router = APIRouter(prefix="/plantas", tags=["plantas"])

#post planta
@router.post(
    "/", 
    response_model=PlantaResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear planta"
)
async def crear_planta(
    request: PlantaCreateRequest,
    service: PlantaService = Depends(get_planta_service)
):
    try:
        planta = await service.crear_planta(nombre=request.nombre, ubicacion=request.ubicacion)
        return PlantaResponse.from_entity(planta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#get plantas
@router.get(
    "/", 
    response_model=List[PlantaResponse],
    summary="Listar todas las plantas"
)
async def listar_plantas(
    service: PlantaService = Depends(get_planta_service)
):
    plantas = await service.obtener_todas()
    return [PlantaResponse.from_entity(p) for p in plantas]
#get planta id
@router.get(
    "/{planta_id}", 
    response_model=PlantaResponse,
    summary="Obtener detalle de planta"
)
async def obtener_planta(
    planta_id: UUID,
    service: PlantaService = Depends(get_planta_service)
):
    planta = await service.obtener_por_id(planta_id)
    if not planta:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    return PlantaResponse.from_entity(planta)

#Obtiene sensores. conexión lógica: Plantas -> Sensores
@router.get("/{planta_id}/sensores", summary="Listar sensores de una planta")
async def listar_sensores_de_planta(
    planta_id: UUID,
    service: PlantaService = Depends(get_planta_service)
):
    # El servicio de planta consulta a su repositorio o al de sensores
    sensores = await service.obtener_sensores_de_planta(planta_id)
    return sensores

#EL IMPORTANTE obtener metricas agregadas mediante sensorservice
@router.get("/{planta_id}/metricas")
async def get_planta_dashboard(planta_id: str, service: SensorService = Depends(get_sensor_service)):
    metricas = await service.obtener_metricas_planta(planta_id)
    return metricas # FastAPI se encarga de serializar los dataclasses