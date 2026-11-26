from fastapi import APIRouter, HTTPException, status

from app.models import (
    AlertResponse,
    DeviceCreate,
    DeviceResponse,
    StatusUpdate,
)
from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)

router = APIRouter()
repository = InMemoryDeviceRepository()
service = DeviceService(repository)


@router.post(
    "/devices",
    status_code=status.HTTP_201_CREATED,
    response_model=DeviceResponse,
    responses={409: {"description": "Device ID already exists"}},
)
def register_device(device: DeviceCreate) -> DeviceResponse:
    try:
        return DeviceResponse.model_validate(
            service.register(device.model_dump())
        )
    except DeviceAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices() -> list[DeviceResponse]:
    return [
        DeviceResponse.model_validate(device) for device in service.list()
    ]


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    responses={404: {"description": "Device not found"}},
)
def get_device(device_id: str) -> DeviceResponse:
    try:
        return DeviceResponse.model_validate(service.get(device_id))
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch(
    "/devices/{device_id}/status",
    response_model=DeviceResponse,
    responses={404: {"description": "Device not found"}},
)
def update_status(
    device_id: str, update: StatusUpdate
) -> DeviceResponse:
    try:
        return DeviceResponse.model_validate(
            service.update_status(device_id, update.status)
        )
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts() -> list[AlertResponse]:
    return [
        AlertResponse.model_validate(alert)
        for alert in repository.list_alerts()
    ]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
