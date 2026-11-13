import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    nifi_url = os.environ["NIFI_BASE_URL"]
    group_id = os.environ["NIFI_PROCESS_GROUP_ID"]

    print(f"NiFi URL: {nifi_url}")
    print(f"Process Group ID: {group_id}")


if __name__ == "__main__":
    main()