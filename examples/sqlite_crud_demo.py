from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import DeviceRow
from app.repositories.sqlalchemy_device_repository import (
    SQLAlchemyDeviceRepository,
)


def main() -> None:
    with TemporaryDirectory(prefix="netpulse-crud-") as directory:
        database_path = Path(directory) / "demo.db"
        engine = create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        session_factory = sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )

        device = {
            "device_id": "DEMO-001",
            "name": "Demo Router",
            "device_type": "router",
            "ip_address": "192.168.10.10",
            "status": "online",
        }
        with session_factory() as session:
            repository = SQLAlchemyDeviceRepository(session)
            repository.add_device(device)
            session.commit()
        print("Create: added DEMO-001 to the temporary database.")

        with session_factory() as session:
            repository = SQLAlchemyDeviceRepository(session)
            print(f"Read: {repository.get_device('DEMO-001')}")
            repository.update_status("DEMO-001", "offline")
            session.commit()
        print("Update: changed DEMO-001 status to offline.")

        with session_factory() as session:
            row = session.get(DeviceRow, "DEMO-001")
            if row is None:
                raise RuntimeError("Demo device disappeared before deletion")
            session.delete(row)
            session.commit()
            print(
                "Delete: DEMO-001 remains? "
                f"{session.get(DeviceRow, 'DEMO-001') is not None}"
            )

        engine.dispose()


if __name__ == "__main__":
    main()
