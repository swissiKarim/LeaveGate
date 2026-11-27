from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="LeaveGate",
    description="Abwesenheitsverwaltung für Mitarbeitende",
    version="0.1.0",
)


@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found"})


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
