"""Entry point of the backend: creates the FastAPI app and registers its endpoints.

Run it with `uv run uvicorn app.main:app --reload` from the `backend/` folder.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.session import DbSession

app = FastAPI(title="SkillGraph API")


@app.get("/health")
def health(session: DbSession) -> JSONResponse:
    """Answers if the server is running and says whether the database is reachable.

    Used by CI, Docker and hosting checks: 200 when everything works, 503 when the
    database can't be reached.
    """
    try:
        session.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse({"status": "error", "database": "unreachable"}, status_code=503)
    return JSONResponse({"status": "ok", "database": "ok"})
