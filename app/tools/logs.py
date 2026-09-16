from pathlib import Path


LOGS_DIR = Path("data/logs")


def search_logs(
    service: str,
    keyword: str | None = None,
) -> list[str]:
    """
    Search service logs.

    Currently reads local log files.
    Later this will query Google Cloud Logging.
    """

    print(
        f"[TOOL] search_logs("
        f"service={service}, "
        f"keyword={keyword!r}"
        f")"
    )

    log_file = LOGS_DIR / f"{service}.log"

    if not log_file.exists():
        return [
            f"No logs available for service: {service}"
        ]

    with log_file.open("r", encoding="utf-8") as file:
        lines = [
            line.strip()
            for line in file
            if line.strip()
        ]

    if keyword is None:
        return lines

    keyword_lower = keyword.lower()

    return [
        line
        for line in lines
        if keyword_lower in line.lower()
    ]