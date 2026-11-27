from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.repositories.sqlalchemy_device_repository import (
    SQLAlchemyDeviceRepository,
)
from app.services.device_service import DeviceService


def get_device_service(
    session: Session = Depends(get_session, scope="function"),
) -> DeviceService:
    return DeviceService(SQLAlchemyDeviceRepository(session))
