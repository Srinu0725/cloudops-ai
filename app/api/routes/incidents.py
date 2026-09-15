from fastapi import APIRouter

from app.models.incident import IncidentRequest


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post("/")
async def create_incident(incident: IncidentRequest):
    return {
        "message": "Incident received",
        "incident": incident.model_dump(),
    }


@router.get("/test")
async def test_incident_route():
    return {
        "message": "Incident API is working",
    }