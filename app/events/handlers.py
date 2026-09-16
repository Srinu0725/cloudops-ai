from typing import Any

from app.incidents.service import incident_store
from app.observability.investigator import (
    IncidentInvestigator,
)


investigator = IncidentInvestigator()


async def handle_incident_created(
    event: dict[str, Any],
) -> None:
    """
    Handle a newly created incident.

    Updates the incident lifecycle as the investigation
    progresses.
    """

    incident_id = event.get(
        "event_id"
    )

    service = event.get(
        "service"
    )

    start_time = event.get(
        "start_time"
    )

    end_time = event.get(
        "end_time"
    )

    print(
        "\n[EVENT HANDLER] "
        f"Starting investigation for {service}"
    )

    # ---------------------------------------------------------
    # Start investigation
    # ---------------------------------------------------------

    incident_store.start_investigation(
        incident_id
    )

    try:

        # -----------------------------------------------------
        # Collect + analyze evidence
        # -----------------------------------------------------

        incident_store.update_stage(
            incident_id,
            "ANALYZING",
        )

        result = investigator.investigate(
            service=service,
            start_time=start_time,
            end_time=end_time,
        )

        # -----------------------------------------------------
        # RCA
        # -----------------------------------------------------

        incident_store.update_stage(
            incident_id,
            "RCA",
        )

        # The RCA is already part of the investigator result.
        # We keep this lifecycle stage explicit because later
        # the investigation engine can expose finer-grained
        # progress events.
        rca_analysis = result.get(
            "rca_analysis"
        )

        if rca_analysis is None:
            print(
                "[EVENT HANDLER] "
                "Warning: RCA analysis missing."
            )

        # -----------------------------------------------------
        # Report
        # -----------------------------------------------------

        incident_store.update_stage(
            incident_id,
            "REPORT_GENERATED",
        )

        final_report = result.get(
            "final_report",
            result,
        )

        incident_store.set_report(
            incident_id,
            final_report,
        )

        print(
            "\n[EVENT HANDLER] "
            "Investigation completed."
        )

        print(
            f"[EVENT HANDLER] Service: {service}"
        )

        print(
            f"[EVENT HANDLER] Incident ID: {incident_id}"
        )

    except Exception as exc:

        incident_store.set_error(
            incident_id,
            str(exc),
        )

        print(
            "\n[EVENT HANDLER] "
            f"Investigation failed: {exc}"
        )

