from fastapi import APIRouter, Depends, status

from app.dependencies import get_device_service
from app.models import (
    AlertResponse,
    DeviceCreate,
    DeviceResponse,
    DeviceProbeResponse,
    DeviceSummaryResponse,
    StatusUpdate,
)
from app.services.device_service import DeviceService
from app.services.probe import simulate_device_probe

router = APIRouter()


@router.post(
    "/devices",
    status_code=status.HTTP_201_CREATED,
    response_model=DeviceResponse,
    responses={409: {"description": "Device ID already exists"}},
)
def register_device(
    device: DeviceCreate,
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> DeviceResponse:
    return DeviceResponse.model_validate(
        service.register(device.model_dump())
    )


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices(
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> list[DeviceResponse]:
    return [
        DeviceResponse.model_validate(device) for device in service.list()
    ]


@router.get(
    "/devices/summary",
    response_model=DeviceSummaryResponse,
)
def get_device_summary(
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> DeviceSummaryResponse:
    return DeviceSummaryResponse.model_validate(
        service.get_device_summary()
    )


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    responses={404: {"description": "Device not found"}},
)
def get_device(
    device_id: str,
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> DeviceResponse:
    return DeviceResponse.model_validate(service.get(device_id))


@router.patch(
    "/devices/{device_id}/status",
    response_model=DeviceResponse,
    responses={404: {"description": "Device not found"}},
)
def update_status(
    device_id: str,
    update: StatusUpdate,
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> DeviceResponse:
    return DeviceResponse.model_validate(
        service.update_status(device_id, update.status)
    )


@router.get(
    "/devices/{device_id}/probe",
    response_model=DeviceProbeResponse,
    responses={404: {"description": "Device not found"}},
)
async def probe_device(
    device_id: str,
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> DeviceProbeResponse:
    service.get_device(device_id)
    return DeviceProbeResponse.model_validate(
        await simulate_device_probe(device_id)
    )


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    service: DeviceService = Depends(get_device_service, scope="function"),
) -> list[AlertResponse]:
    return [
        AlertResponse.model_validate(alert)
        for alert in service.list_alerts()
    ]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
