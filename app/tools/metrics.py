import json
from pathlib import Path


METRICS_DIR = Path("data/metrics")


def get_service_metrics(service: str) -> dict:
    """
    Retrieve metrics for a service.

    Currently reads mock metrics from local JSON files.
    Later this will query Google Cloud Monitoring.
    """

    metrics_file = METRICS_DIR / f"{service}.json"

    if not metrics_file.exists():
        return {
            "error": f"No metrics available for service: {service}"
        }

    try:
        with metrics_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return {
            "error": f"Invalid metrics data for service: {service}"
        }