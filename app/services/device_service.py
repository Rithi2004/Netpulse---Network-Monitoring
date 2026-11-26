from typing import Any

from app.events import create_offline_alert
from app.repositories.device_repository import InMemoryDeviceRepository


class DeviceAlreadyExistsError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass


class DeviceService:
    def __init__(self, repository: InMemoryDeviceRepository) -> None:
        self.repository = repository

    def register(self, device: dict[str, Any]) -> dict[str, Any]:
        if self.repository.get_device(device["device_id"]) is not None:
            raise DeviceAlreadyExistsError(
                f"Device {device['device_id']} already exists"
            )
        return self.repository.add_device(device)

    def list(self) -> list[dict[str, Any]]:
        return self.repository.list_devices()

    def get(self, device_id: str) -> dict[str, Any]:
        device = self.repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(f"Device {device_id} not found")
        return device

    def update_status(
        self, device_id: str, status: str
    ) -> dict[str, Any]:
        device = self.repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(f"Device {device_id} not found")

        previous_status = device["status"]
        if previous_status == "online" and status == "offline":
            create_offline_alert(self.repository, device_id)

        updated = self.repository.update_status(device_id, status)
        if updated is None:
            raise DeviceNotFoundError(f"Device {device_id} not found")
        return updated
