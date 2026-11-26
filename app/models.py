import ipaddress
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class ValidatedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DeviceCreate(ValidatedModel):
    device_id: str
    name: str
    device_type: Literal["router", "switch", "server"]
    ip_address: str
    status: Literal["online", "offline"] = "online"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, value: str) -> str:
        try:
            address = ipaddress.ip_address(value)
        except ValueError as exc:
            raise ValueError("ip_address must be a valid IPv4 address") from exc
        if address.version != 4:
            raise ValueError("ip_address must be a valid IPv4 address")
        return str(address)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "device_id": "RTR-101",
                "name": "Branch Router",
                "device_type": "router",
                "ip_address": "192.168.10.1",
                "status": "online",
            }
        },
    )


class DeviceResponse(ValidatedModel):
    device_id: str
    name: str
    device_type: Literal["router", "switch", "server"]
    ip_address: str
    status: Literal["online", "offline"]


class StatusUpdate(ValidatedModel):
    status: Literal["online", "offline"]

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"status": "offline"}},
    )


class AlertResponse(ValidatedModel):
    device_id: str
    message: str
    timestamp: datetime


class DeviceSummaryResponse(ValidatedModel):
    total_devices: int
    online_count: int
    offline_count: int
    device_types: list[str]


class DeviceProbeResponse(ValidatedModel):
    device_id: str
    reachable: bool
    simulated: bool
