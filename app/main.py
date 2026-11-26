from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routes.devices import router
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
)

app = FastAPI(
    title="NetPulse Network Monitoring API",
    description="In-memory network device monitoring",
)
app.include_router(router)


@app.exception_handler(DeviceAlreadyExistsError)
async def device_already_exists_handler(
    request, exc: DeviceAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DeviceNotFoundError)
async def device_not_found_handler(
    request, exc: DeviceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
