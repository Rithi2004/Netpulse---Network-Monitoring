# NetPulse

NetPulse is a layered FastAPI network device monitoring API backed by SQLite
and SQLAlchemy. Device and alert records are stored in `netpulse.db` in the
project root and survive application restarts.

Start it from the project root:

```bash
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI or `http://127.0.0.1:8000/openapi.json`.

Uvicorn is the ASGI server that runs the FastAPI ASGI application. ASGI supports
asynchronous endpoints, including the simulated device probe. Most database
routes are synchronous `def` handlers, so FastAPI runs their SQLAlchemy work in
a worker thread rather than blocking the async event loop. The async probe
handler performs a synchronous existence lookup before awaiting its simulated
probe; this is a small-lab trade-off. ASGI supports asynchronous applications,
unlike the older synchronous WSGI interface.

Run the isolated CRUD demonstration with:

```bash
python -m examples.sqlite_crud_demo
```

Tests use temporary SQLite databases and do not modify the project database.
