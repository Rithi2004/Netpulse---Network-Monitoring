from datetime import datetime, timezone
from typing import Any

from app.repositories.device_repository import InMemoryDeviceRepository


def create_offline_alert(
    repository: InMemoryDeviceRepository, device_id: str
) -> dict[str, Any]:
    alert = {
        "device_id": device_id,
        "message": f"Device {device_id} changed from online to offline",
        "timestamp": datetime.now(timezone.utc),
    }
    return repository.save_alert(alert)
