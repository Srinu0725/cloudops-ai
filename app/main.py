from fastapi import FastAPI

from app.config import settings
from app.api.routes.incidents import router as incidents_router


app = FastAPI(
    title=settings.app_name,
    description=(
        "Agentic AI platform for automated "
        "production incident investigation."
    ),
    version="0.1.0",
)


app.include_router(incidents_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }