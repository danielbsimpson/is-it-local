"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.routers import businesses

app = FastAPI(
    title="Is It Local API",
    version="0.1.0",
    description="Serves businesses with ownership classifications, confidence, and sources.",
)

app.include_router(businesses.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
