from copy import deepcopy
from typing import Any


class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[str, dict[str, Any]] = {}
        self._alerts: list[dict[str, Any]] = []

    def add_device(self, device: dict[str, Any]) -> dict[str, Any]:
        device_id = device["device_id"]
        if device_id in self._devices:
            raise ValueError("device_id already exists")
        stored = deepcopy(device)
        self._devices[device_id] = stored
        return deepcopy(stored)

    def list_devices(self) -> list[dict[str, Any]]:
        return deepcopy(list(self._devices.values()))

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        device = self._devices.get(device_id)
        return deepcopy(device) if device is not None else None

    def update_status(self, device_id: str, status: str) -> dict[str, Any] | None:
        device = self._devices.get(device_id)
        if device is None:
            return None
        device["status"] = status
        return deepcopy(device)

    def save_alert(self, alert: dict[str, Any]) -> dict[str, Any]:
        stored = deepcopy(alert)
        self._alerts.append(stored)
        return deepcopy(stored)

    def list_alerts(self) -> list[dict[str, Any]]:
        return deepcopy(self._alerts)
