from fastapi import FastAPI

from app.routes.devices import router

app = FastAPI(
    title="NetPulse Network Monitoring API",
    description="In-memory network device monitoring",
)
app.include_router(router)
