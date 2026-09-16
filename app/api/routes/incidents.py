from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.events.models import IncidentEvent
from app.events.service import event_queue
from app.incidents.service import incident_store


router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)


# =========================================================
# Request Models
# =========================================================


class CreateIncidentRequest(BaseModel):
    """
    Request body for creating a new production incident.
    """

    service: str = Field(
        ...,
        min_length=1,
        description="Affected service name.",
    )

    description: str = Field(
        ...,
        min_length=1,
        description="Description of the incident.",
    )

    severity: str = Field(
        default="unknown",
        description="Incident severity.",
    )

    start_time: str | None = Field(
        default=None,
        description="Start of the investigation window.",
    )

    end_time: str | None = Field(
        default=None,
        description="End of the investigation window.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional incident metadata.",
    )


# =========================================================
# Create Incident
# =========================================================


@router.post(
    "",
    status_code=202,
)
async def create_incident(
    request: CreateIncidentRequest,
):
    """
    Create a new incident and enqueue it for investigation.

    The API does not perform the investigation itself.
    It creates the incident, stores its initial state,
    and places an incident.created event onto the queue.
    """

    # -----------------------------------------------------
    # Create incident event
    # -----------------------------------------------------

    event = IncidentEvent.create(
        service=request.service,
        description=request.description,
        severity=request.severity,
        start_time=request.start_time,
        end_time=request.end_time,
        metadata=request.metadata,
    )

    # -----------------------------------------------------
    # Create initial incident state
    # -----------------------------------------------------

    incident = incident_store.create(
        incident_id=event.event_id,
        service=event.service,
        severity=event.severity,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        metadata=event.metadata,
    )

    # -----------------------------------------------------
    # Publish event to queue
    # -----------------------------------------------------

    await event_queue.publish(
        event.to_dict()
    )

    # -----------------------------------------------------
    # Return immediately
    # -----------------------------------------------------

    return {
        "incident_id": event.event_id,
        "status": incident.status,
        "message": (
            "Incident created and queued "
            "for investigation."
        ),
    }


# =========================================================
# Get Incident Status
# =========================================================


@router.get(
    "/{incident_id}/status",
)
async def get_incident_status(
    incident_id: str,
):
    """
    Return lightweight incident lifecycle information.

    Possible statuses:

    CREATED
    INVESTIGATING
    COMPLETED
    FAILED
    """

    incident = incident_store.get(
        incident_id
    )

    if incident is None:

        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    return {
        "incident_id": incident.incident_id,

        "service": incident.service,

        "status": incident.status,

        "stage": incident.stage,

        "created_at": incident.created_at,

        "started_at": incident.started_at,

        "completed_at": incident.completed_at,

        "failed_at": incident.failed_at,

        "error": incident.error,
    }


# =========================================================
# Get Complete Incident
# =========================================================


@router.get(
    "/{incident_id}",
)
async def get_incident(
    incident_id: str,
):
    """
    Retrieve the complete incident state.

    Once the investigation is completed, the response
    also contains the final incident report.
    """

    incident = incident_store.get(
        incident_id
    )

    if incident is None:

        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    return incident.to_dict()

