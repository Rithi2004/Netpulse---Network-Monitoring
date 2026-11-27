from datetime import timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AlertRow, DeviceRow


class SQLAlchemyDeviceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_device(self, device: dict[str, Any]) -> dict[str, Any]:
        row = DeviceRow(**device)
        self.session.add(row)
        self.session.flush()
        return self._device_to_dict(row)

    def list_devices(self) -> list[dict[str, Any]]:
        rows = self.session.scalars(select(DeviceRow)).all()
        return [self._device_to_dict(row) for row in rows]

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        row = self.session.get(DeviceRow, device_id)
        return self._device_to_dict(row) if row is not None else None

    def update_status(
        self, device_id: str, status: str
    ) -> dict[str, Any] | None:
        row = self.session.get(DeviceRow, device_id)
        if row is None:
            return None
        row.status = status
        self.session.flush()
        return self._device_to_dict(row)

    def save_alert(self, alert: dict[str, Any]) -> dict[str, Any]:
        row = AlertRow(**alert)
        self.session.add(row)
        self.session.flush()
        return self._alert_to_dict(row)

    def list_alerts(self) -> list[dict[str, Any]]:
        rows = self.session.scalars(
            select(AlertRow).order_by(AlertRow.id)
        ).all()
        return [self._alert_to_dict(row) for row in rows]

    @staticmethod
    def _device_to_dict(row: DeviceRow) -> dict[str, Any]:
        return {
            "device_id": row.device_id,
            "name": row.name,
            "device_type": row.device_type,
            "ip_address": row.ip_address,
            "status": row.status,
        }

    @staticmethod
    def _alert_to_dict(row: AlertRow) -> dict[str, Any]:
        timestamp = row.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return {
            "device_id": row.device_id,
            "message": row.message,
            "timestamp": timestamp,
        }
