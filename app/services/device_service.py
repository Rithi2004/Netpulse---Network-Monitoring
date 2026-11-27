from typing import Any

from app.events import create_offline_alert
from app.repositories.contracts import DeviceRepository


class DeviceAlreadyExistsError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass


class DeviceService:
    def __init__(self, repository: DeviceRepository) -> None:
        self.repository = repository

    def register(self, device: dict[str, Any]) -> dict[str, Any]:
        if self.repository.get_device(device["device_id"]) is not None:
            raise DeviceAlreadyExistsError(
                f"Device {device['device_id']} already exists"
            )
        return self.repository.add_device(device)

    def list_alerts(self) -> list[dict[str, Any]]:
        return self.repository.list_alerts()

    def list(self) -> list[dict[str, Any]]:
        return self.repository.list_devices()

    def get(self, device_id: str) -> dict[str, Any]:
        device = self.repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(f"Device {device_id} not found")
        return device

    def get_device(self, device_id: str) -> dict[str, Any]:
        return self.get(device_id)

    def get_device_summary(self) -> dict[str, Any]:
        devices = self.repository.list_devices()
        online_count = sum(
            1 for device in devices if device["status"] == "online"
        )
        offline_count = sum(
            1 for device in devices if device["status"] == "offline"
        )
        device_types = sorted(
            {device["device_type"] for device in devices}
        )
        return {
            "total_devices": len(devices),
            "online_count": online_count,
            "offline_count": offline_count,
            "device_types": device_types,
        }

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
