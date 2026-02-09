"""
Endpoints REST para telemetría
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.infra.adapters.rest.schemas.telemetria import TelemetriaCreateRequest, TelemetriaLoteRequest, TelemetriaResponse, TelemetriaSimpleResponse
from application.services.telemetria_service import TelemetriaService
from infra.config.inyeccion_dependencias import get_telemetria_service


router = APIRouter(prefix="/telemetria", tags=["telemetría"])

# METER DATOS Y GENERA HASH
@router.post(
    "/",
    response_model=TelemetriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar telemetría",
    description="Registra una nueva lectura de telemetría"
)
async def registrar_telemetria(
    request: TelemetriaCreateRequest,
    service: TelemetriaService = Depends(get_telemetria_service)
):
    try:
        telemetria = await service.registrar_lectura(
            sensor_id=request.sensor_id,
            valor=request.valor
        )
        return TelemetriaResponse.from_entity(telemetria)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

#ahorra bateria conexion
@router.post(
    "/lote",
    response_model=List[TelemetriaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar telemetría en lote",
    description="Registra múltiples lecturas de telemetría en una sola operación"
)
async def registrar_telemetria_lote(
    request: TelemetriaLoteRequest,
    service: TelemetriaService = Depends(get_telemetria_service)
):
    try:
        # Convertir a dict o lista de tuplas sensor_id/valor
        lecturas = [(l.sensor_id, l.valor) for l in request.lecturas]

        # Método nuevo en TelemetriaService
        resultados = await service.registrar_lecturas_lote(lecturas)

        return [TelemetriaResponse.from_entity(t) for t in resultados]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error registrando telemetría en lote: {str(e)}"
        )

# GET ID 
@router.get(
    "/{telemetria_id}",
    response_model=TelemetriaResponse,
    summary="Obtener telemetría por ID",
)
async def obtener_telemetria(
    telemetria_id: UUID,
    service: TelemetriaService = Depends(get_telemetria_service)
):
    try:
        telemetria = await service.obtener_por_id(telemetria_id)
        return TelemetriaResponse.from_entity(telemetria)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

#  GET ultimas DE UN SENSOR -> lista valores y fechas   con  limite de datos solicitados para que evite caida servidor
@router.get(
    "/sensor/{sensor_id}/ultimas",
    response_model=List[TelemetriaSimpleResponse],
    summary="Obtener últimas telemetrías",
    description="Obtiene las últimas N telemetrías de un sensor"
)
async def obtener_ultimas_telemetrias(
    sensor_id: UUID,
    limite: int = Query(10, ge=1, le=1000, description="Número de telemetrías a obtener"),
    service: TelemetriaService = Depends(get_telemetria_service)
):
    try:
        telemetrias, sensor = await service.obtener_lecturas_con_info_sensor(sensor_id, limite=limite)
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor no encontrado")
        return [
            TelemetriaSimpleResponse.from_entity(t, unidad=sensor.unidad)
            for t in telemetrias
        ]
    except HTTPException:
        # Re-lanzamos la excepción de FastAPI tal cual para que no caiga en el 500
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo telemetrías: {str(e)}"
        )

