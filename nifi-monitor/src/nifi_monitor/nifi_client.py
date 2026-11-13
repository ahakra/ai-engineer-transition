
import os
import typing
import httpx


def get_access_token() -> str:
    base_url = os.environ["NIFI_BASE_URL"].rstrip("/")
    username = os.environ["NIFI_USERNAME"]
    password = os.environ["NIFI_PASSWORD"]

    with httpx.Client(
        verify=False,  # Local self-signed NiFi lab only
        timeout=10.0,
    ) as client:
        response = client.post(
            f"{base_url}/nifi-api/access/token",
            data={
                "username": username,
                "password": password,
            },
        )
        response.raise_for_status()
        return response.text.strip()


def get_processors(token: str) -> list[dict[str, object]]:
    base_url = os.environ["NIFI_BASE_URL"].rstrip("/")
    group_id = os.environ["NIFI_PROCESS_GROUP_ID"]

    with httpx.Client(verify=False, timeout=10.0) as client:
        response = client.get(
            f"{base_url}/nifi-api/process-groups/{group_id}/processors",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()["processors"]



def get_processor_info(token: str, id: str) -> dict[str, typing.Any]:
    base_url = os.environ["NIFI_BASE_URL"].rstrip("/")

    with httpx.Client(verify=False, timeout=10.0) as client:
        response = client.get(
            f"{base_url}/nifi-api/processors/{id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()

        data = response.json()

        component = data.get("component") or {}
        status = data.get("status") or {}
        snapshot = status.get("aggregateSnapshot") or {}

        return {
            "id": data.get("id"),
            "name": component.get("name"),
            "state": component.get("state"),
            "physical_state": data.get("physicalState"),
            "input": {
                "flowfiles": snapshot.get("flowFilesIn", 0),
                "bytes": snapshot.get("bytesIn", 0),
            },
            "output": {
                "flowfiles": snapshot.get("flowFilesOut", 0),
                "bytes": snapshot.get("bytesOut", 0),
            },
            "bulletins": data.get("bulletins", []),
        }



def get_processor_status(token: str, id: str) -> dict[str, typing.Any]:
    base_url = os.environ["NIFI_BASE_URL"].rstrip("/")

    with httpx.Client(verify=False, timeout=10.0) as client:
        response = client.get(
            f"{base_url}/nifi-api/flow/processors/{id}/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()

        data = response.json()
        return  data
