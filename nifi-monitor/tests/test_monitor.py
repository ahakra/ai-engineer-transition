"""Offline tests for presentation and the REST contract."""

import httpx
import pytest

from nifi_monitor.main import format_table, show_processor_status
from nifi_monitor.nifi_client import get_processor_status, get_processors


def test_format_table() -> None:
    result = format_table(("Name", "State"), [("ValidateJson", "STOPPED")])
    assert "Name         | State" in result
    assert "ValidateJson | STOPPED" in result


def test_format_table_rejects_misaligned_rows() -> None:
    with pytest.raises(ValueError, match="row"):
        format_table(("Name", "State"), [("ValidateJson",)])


def test_missing_metric_not_reported_as_zero(capsys: pytest.CaptureFixture[str]) -> None:
    show_processor_status(
        {"processorStatus": {"name": "ValidateJson", "aggregateSnapshot": {}}}
    )
    output = capsys.readouterr().out
    assert "N/A" in output
    assert "FlowFiles in" in output


def test_missing_status_is_an_error() -> None:
    with pytest.raises(ValueError, match="processorStatus"):
        show_processor_status({})


def test_read_only_status_endpoint_and_bearer_header() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/processors"):
            return httpx.Response(
                200,
                json={
                    "processors": [
                        {"component": {"id": "p1", "name": "ValidateJson", "state": "STOPPED"}}
                    ]
                },
            )
        return httpx.Response(
            200,
            json={
                "processorStatus": {
                    "name": "ValidateJson",
                    "runStatus": "Stopped",
                    "aggregateSnapshot": {"flowFilesIn": 0, "flowFilesOut": 0},
                }
            },
        )

    with httpx.Client(
        base_url="https://nifi.example",
        transport=httpx.MockTransport(respond),
    ) as client:
        processors = get_processors(client, "fake-token", "group-1")
        status = get_processor_status(client, "fake-token", "p1")

    assert processors[0]["component"]["name"] == "ValidateJson"
    assert status["processorStatus"] is not None
    assert [request.method for request in requests] == ["GET", "GET"]
    assert requests[1].url.path == "/nifi-api/flow/processors/p1/status"
    assert all(request.headers["Authorization"] == "Bearer fake-token" for request in requests)
