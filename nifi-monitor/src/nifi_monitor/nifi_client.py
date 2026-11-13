"""Minimal read-only NiFi REST calls; authentication is the only POST."""

import os
from typing import TypedDict, cast

import httpx


class ProcessorComponent(TypedDict):
    id: str
    name: str
    state: str


class ProcessorEntity(TypedDict):
    component: ProcessorComponent


def get_access_token(client: httpx.Client) -> str:
    """Authenticate against NiFi. Never log the returned bearer token."""
    response = client.post(
        "/nifi-api/access/token",
        data={
            "username": os.environ["NIFI_USERNAME"],
            "password": os.environ["NIFI_PASSWORD"],
        },
    )
    response.raise_for_status()
    token = response.text.strip()
    if not token:
        raise ValueError("NiFi returned an empty access token")
    return token


def get_processors(
    client: httpx.Client, token: str, group_id: str
) -> list[ProcessorEntity]:
    """Return processor names, IDs and configured states."""
    response = client.get(
        f"/nifi-api/process-groups/{group_id}/processors",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    data = response.json()
    # At the HTTP/JSON boundary, a typed declaration does not validate the
    # remote server response. Runtime schema validation comes in a later task.
    return cast(list[ProcessorEntity], data["processors"])


def get_processor_status(
    client: httpx.Client, token: str, processor_id: str
) -> dict[str, object]:
    """Return a processor's status entity (not its configuration entity)."""
    response = client.get(
        f"/nifi-api/flow/processors/{processor_id}/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    data: dict[str, object] = response.json()
    return data
