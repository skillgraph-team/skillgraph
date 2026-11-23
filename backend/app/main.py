"""Entry point of the backend: creates the FastAPI app and registers its endpoints.

Run it with `uv run uvicorn app.main:app --reload` from the `backend/` folder.
"""

from fastapi import FastAPI

app = FastAPI(title="SkillGraph API")


@app.get("/health")
def health() -> dict[str, str]:
    """Answers if the server is running. Used by CI, Docker and hosting checks."""
    return {"status": "ok"}
