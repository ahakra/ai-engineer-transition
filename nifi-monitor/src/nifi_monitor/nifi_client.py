
import os

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
