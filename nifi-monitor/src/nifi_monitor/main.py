
import os
from pathlib import Path

from dotenv import load_dotenv

from nifi_monitor.nifi_client import get_access_token, get_processors,get_processor_info,get_processor_status

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    nifi_url = os.environ["NIFI_BASE_URL"]
    group_id = os.environ["NIFI_PROCESS_GROUP_ID"]

    print(f"NiFi URL: {nifi_url}")
    print(f"Process Group ID: {group_id}")

    token = get_access_token()
    print("Authentication successful:", bool(token))

    processors = get_processors(token)
    validateJsonInfo = ""
    validateJsonStatus=""
    for processor in processors:
        component = processor["component"]
        print(component["name"], component["state"],component["id"])
        if component["name"] == "ValidateJson":
            validateJsonInfo = get_processor_info(token,component["id"])
            validateJsonStatus = get_processor_status(token,component["id"])

    print(validateJsonInfo)
    print(validateJsonStatus)
if __name__ == "__main__":
    main()
