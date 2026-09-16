from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class IncidentState:
    """
    Represents the lifecycle state of an incident investigation.
    """

    incident_id: str

    service: str

    status: str = "CREATED"

    stage: str = "CREATED"

    severity: str = "unknown"

    description: str = ""

    start_time: str | None = None

    end_time: str | None = None

    created_at: str = field(
        default_factory=utc_now
    )

    started_at: str | None = None

    completed_at: str | None = None

    failed_at: str | None = None

    report: dict[str, Any] | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def start_investigation(self) -> None:
        """
        Mark the investigation as started.
        """

        self.status = "INVESTIGATING"

        self.stage = "COLLECTING_EVIDENCE"

        self.started_at = utc_now()

    def update_stage(
        self,
        stage: str,
    ) -> None:
        """
        Update the current investigation stage.
        """

        self.stage = stage

    def complete(
        self,
        report: dict[str, Any],
    ) -> None:
        """
        Mark the investigation as completed.
        """

        self.status = "COMPLETED"

        self.stage = "REPORT_GENERATED"

        self.report = report

        self.completed_at = utc_now()

    def fail(
        self,
        error: str,
    ) -> None:
        """
        Mark the investigation as failed.
        """

        self.status = "FAILED"

        self.stage = "FAILED"

        self.error = error

        self.failed_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize incident state.
        """

        return {
            "incident_id": self.incident_id,

            "service": self.service,

            "status": self.status,

            "stage": self.stage,

            "severity": self.severity,

            "description": self.description,

            "start_time": self.start_time,

            "end_time": self.end_time,

            "created_at": self.created_at,

            "started_at": self.started_at,

            "completed_at": self.completed_at,

            "failed_at": self.failed_at,

            "report": self.report,

            "error": self.error,

            "metadata": self.metadata,
        }

