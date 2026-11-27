from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.db.database as database_module
import app.main as main_module
from app.db.database import Base, get_session
from app.db.models import AlertRow, DeviceRow
from app.repositories.sqlalchemy_device_repository import (
    SQLAlchemyDeviceRepository,
)
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)


@pytest.fixture
def database(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    monkeypatch.setattr(database_module, "SessionLocal", factory)
    monkeypatch.setattr(main_module, "engine", engine)
    yield factory
    engine.dispose()


def sample_device() -> dict[str, str]:
    return {
        "device_id": "RTR-101",
        "name": "Branch Router",
        "device_type": "router",
        "ip_address": "192.168.10.1",
        "status": "online",
    }


def test_repository_crud_and_persistence_across_sessions(
    database: sessionmaker[Session],
) -> None:
    with database() as session:
        repository = SQLAlchemyDeviceRepository(session)
        assert repository.add_device(sample_device()) == sample_device()
        session.commit()

    with database() as session:
        repository = SQLAlchemyDeviceRepository(session)
        assert repository.get_device("RTR-101") == sample_device()
        assert repository.list_devices() == [sample_device()]
        updated = repository.update_status("RTR-101", "offline")
        assert updated is not None
        assert updated["status"] == "offline"
        session.commit()

    with database() as session:
        assert session.get(DeviceRow, "RTR-101").status == "offline"


def test_service_errors_summary_and_offline_alert_rule(
    database: sessionmaker[Session],
) -> None:
    with database() as session:
        service = DeviceService(SQLAlchemyDeviceRepository(session))
        service.register(sample_device())
        with pytest.raises(DeviceAlreadyExistsError):
            service.register(sample_device())
        with pytest.raises(DeviceNotFoundError):
            service.get("RTR-404")
        with pytest.raises(DeviceNotFoundError):
            service.update_status("RTR-404", "offline")

        assert service.get_device_summary() == {
            "total_devices": 1,
            "online_count": 1,
            "offline_count": 0,
            "device_types": ["router"],
        }
        service.update_status("RTR-101", "offline")
        service.update_status("RTR-101", "offline")
        session.commit()

    with database() as session:
        repository = SQLAlchemyDeviceRepository(session)
        alerts = repository.list_alerts()
        assert len(alerts) == 1
        assert alerts[0]["device_id"] == "RTR-101"
        assert alerts[0]["timestamp"].tzinfo is not None


def test_get_session_rolls_back_status_and_alert_together(
    database: sessionmaker[Session],
) -> None:
    with database() as session:
        SQLAlchemyDeviceRepository(session).add_device(sample_device())
        session.commit()

    request_session = get_session()
    session = next(request_session)
    service = DeviceService(SQLAlchemyDeviceRepository(session))
    service.update_status("RTR-101", "offline")

    with pytest.raises(RuntimeError, match="simulated failure"):
        request_session.throw(RuntimeError("simulated failure"))

    with database() as verification_session:
        device = verification_session.get(DeviceRow, "RTR-101")
        assert device is not None
        assert device.status == "online"
        assert verification_session.query(AlertRow).count() == 0


def test_api_uses_persistent_sqlite_storage_and_preserves_endpoints(
    database: sessionmaker[Session],
) -> None:
    payload = sample_device()
    with TestClient(main_module.app) as client:
        created = client.post("/devices", json=payload)
        assert created.status_code == 201
        assert client.get("/devices").json() == [payload]
        assert client.get("/devices/RTR-101").json() == payload
        assert client.get("/devices/summary").json() == {
            "total_devices": 1,
            "online_count": 1,
            "offline_count": 0,
            "device_types": ["router"],
        }
        assert client.patch(
            "/devices/RTR-101/status", json={"status": "offline"}
        ).status_code == 200
        assert client.patch(
            "/devices/RTR-101/status", json={"status": "offline"}
        ).status_code == 200
        assert len(client.get("/alerts").json()) == 1
        assert client.get("/devices/RTR-101/probe").json() == {
            "device_id": "RTR-101",
            "reachable": True,
            "simulated": True,
        }
        assert client.get("/health").json() == {"status": "ok"}

    with TestClient(main_module.app) as client:
        assert client.get("/devices/RTR-101").json()["status"] == "offline"
        assert len(client.get("/alerts").json()) == 1
        assert client.post("/devices", json=payload).status_code == 409
        assert client.get("/devices/RTR-404").status_code == 404
        invalid_payload = {**payload, "ip_address": "not-an-ip"}
        assert client.post("/devices", json=invalid_payload).status_code == 422
