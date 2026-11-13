"""Command-line entry point for inspecting the NiFi lab (read-only)."""

import os
from collections.abc import Sequence
from pathlib import Path

import httpx
from dotenv import load_dotenv

from nifi_monitor.nifi_client import (
    get_access_token,
    get_processor_status,
    get_processors,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def format_table(headers: tuple[str, ...], rows: Sequence[tuple[str, ...]]) -> str:
    """Format small terminal tables without adding a UI dependency."""
    if any(len(row) != len(headers) for row in rows):
        raise ValueError("Every table row must match the header width")

    widths = [
        max(len(header), *(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]

    def render(row: tuple[str, ...]) -> str:
        return " | ".join(
            value.ljust(width) for value, width in zip(row, widths, strict=True)
        )

    separator = "-+-".join("-" * width for width in widths)
    return "\n".join([render(headers), separator, *(render(row) for row in rows)])


def show_processor_status(status: dict[str, object]) -> None:
    """Display available metrics; missing metrics are NOT zero."""
    processor_status = status.get("processorStatus")
    if not isinstance(processor_status, dict):
        raise ValueError("NiFi response is missing processorStatus")

    snapshot = processor_status.get("aggregateSnapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("NiFi response is missing aggregateSnapshot")

    def display(value: object) -> str:
        return "N/A" if value is None else str(value)

    rows = [
        ("Name", display(processor_status.get("name"))),
        ("Run status", display(processor_status.get("runStatus"))),
        ("FlowFiles in", display(snapshot.get("flowFilesIn"))),
        ("Bytes in", display(snapshot.get("bytesIn"))),
        ("FlowFiles out", display(snapshot.get("flowFilesOut"))),
        ("Bytes out", display(snapshot.get("bytesOut"))),
    ]
    print("\nValidateJson runtime status (NiFi reporting window)")
    print(format_table(("Metric", "Value"), rows))


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    base_url = os.environ["NIFI_BASE_URL"].rstrip("/")
    group_id = os.environ["NIFI_PROCESS_GROUP_ID"]

    # The lab uses a self-signed certificate. Do NOT disable TLS verification
    # outside this local, trusted lab; install and trust its CA instead.
    with httpx.Client(base_url=base_url, verify=False, timeout=10.0) as client:
        token = get_access_token(client)
        processors = get_processors(client, token, group_id)

        rows: list[tuple[str, str, str]] = []
        validator_id: str | None = None

        for processor in processors:
            component = processor["component"]
            rows.append((component["name"], component["state"], component["id"]))
            if component["name"] == "ValidateJson":
                validator_id = component["id"]

        print(f"NiFi: {base_url} | Process Group: {group_id}")
        print("\nProcessors")
        print(format_table(("Name", "State", "ID"), rows))

        if validator_id is None:
            raise RuntimeError("ValidateJson is missing from the configured group")

        show_processor_status(get_processor_status(client, token, validator_id))


if __name__ == "__main__":
    main()
