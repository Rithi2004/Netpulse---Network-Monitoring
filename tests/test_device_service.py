import pytest
import asyncio

from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.probe import simulate_device_probe
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)


@pytest.fixture
def service() -> DeviceService:
    return DeviceService(InMemoryDeviceRepository())


def online_device() -> dict:
    return {
        "device_id": "RTR-101",
        "name": "Branch Router",
        "device_type": "router",
        "ip_address": "192.168.10.1",
        "status": "online",
    }


def test_registration(service: DeviceService) -> None:
    registered = service.register(online_device())

    assert registered == online_device()
    assert service.list() == [online_device()]


def test_duplicate_registration(service: DeviceService) -> None:
    service.register(online_device())

    with pytest.raises(DeviceAlreadyExistsError):
        service.register(online_device())


def test_missing_device(service: DeviceService) -> None:
    with pytest.raises(DeviceNotFoundError):
        service.get("RTR-404")

    with pytest.raises(DeviceNotFoundError):
        service.update_status("RTR-404", "offline")


def test_initial_offline_registration_creates_no_alert(
    service: DeviceService,
) -> None:
    device = online_device()
    device["status"] = "offline"
    service.register(device)

    assert service.repository.list_alerts() == []


def test_online_to_offline_creates_one_alert(
    service: DeviceService,
) -> None:
    service.register(online_device())

    updated = service.update_status("RTR-101", "offline")

    assert updated["status"] == "offline"
    alerts = service.repository.list_alerts()
    assert len(alerts) == 1
    assert alerts[0]["device_id"] == "RTR-101"


def test_repeated_offline_still_creates_one_alert(
    service: DeviceService,
) -> None:
    service.register(online_device())
    service.update_status("RTR-101", "offline")

    service.update_status("RTR-101", "offline")

    assert len(service.repository.list_alerts()) == 1


def test_empty_device_summary(service: DeviceService) -> None:
    assert service.get_device_summary() == {
        "total_devices": 0,
        "online_count": 0,
        "offline_count": 0,
        "device_types": [],
    }


def test_populated_summary_uses_unique_sorted_device_types(
    service: DeviceService,
) -> None:
    service.register(online_device())
    switch = {
        "device_id": "SW-102",
        "name": "Floor Switch",
        "device_type": "switch",
        "ip_address": "192.168.10.2",
        "status": "online",
    }
    service.register(switch)
    service.update_status("RTR-101", "offline")

    assert service.get_device_summary() == {
        "total_devices": 2,
        "online_count": 1,
        "offline_count": 1,
        "device_types": ["router", "switch"],
    }


def test_simulated_probe() -> None:
    result = asyncio.run(simulate_device_probe("RTR-101"))

    assert result["device_id"] == "RTR-101"
    assert result["reachable"] is True
    assert result["simulated"] is True
