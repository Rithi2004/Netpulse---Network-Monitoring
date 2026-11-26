import pytest

from app.repositories.device_repository import InMemoryDeviceRepository
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
