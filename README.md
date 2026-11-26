# NetPulse

NetPulse is a layered, in-memory FastAPI network device monitoring API.

Start it from the project root:

```bash
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI or `http://127.0.0.1:8000/openapi.json`.

Device and alert data are kept in memory only. Restarting the server clears all registered devices and alerts.
