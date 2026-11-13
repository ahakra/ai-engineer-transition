# Local development services

These Compose files are **independent**. For milestone M0, start **NiFi only**. PostgreSQL, pgAdmin, Ollama, and Open WebUI are optional general infrastructure reserved for later experiments; do not start them to complete M0.

## Apache NiFi — M0.1

Run commands from the **repository root** on a system with Docker Engine, Docker Compose v2, Make and curl installed.

```sh
git pull
cp .env.example .env  # Only on first setup: do not overwrite an existing .env
```

Edit `.env`, especially `NIFI_PASSWORD` (use a unique password of **at least 12 characters**, not the sample placeholder). Keep `.env` out of Git.

```sh
make nifi-config       # Docker Compose YAML/environment validation
make nifi-pull         # Download pinned apache/nifi:2.12.0 image
make nifi-up           # Start only NiFi
make nifi-ps           # Confirm container is running
make nifi-logs         # Follow startup logs; Ctrl+C stops following, not NiFi
```

The UI is at **https://localhost:8443/nifi/** (use `NIFI_PORT` from `.env` if changed). Self-signed TLS is expected in this isolated local lab; inspect/accept the browser certificate warning only for this known local instance. Authenticate using your `NIFI_USERNAME` and `NIFI_PASSWORD` values.

### Readiness verification

A running container is **not** evidence that NiFi has finished starting. After `make nifi-up`, check the HTTPS endpoint (change `8443` if `NIFI_PORT` differs):

```sh
curl --insecure --silent --show-error --output /dev/null --write-out 'HTTP %{http_code}\n' https://127.0.0.1:8443/nifi/
```

A successful HTTP response or login redirect confirms the web endpoint responds. `000`, connection failures, or 5xx errors mean it is not ready or has a problem. Also **log in through the NiFi UI** before declaring the lab ready. Verify basic functionality after a restart to confirm persisted configuration. The curl command disables certificate verification **only for this local self-signed lab**, not production.

Stop NiFi without deleting named volumes:

```sh
make nifi-down
```

Then restart with `make nifi-up` to check persistence. Do not use `docker compose down -v` unless you intentionally want to delete the lab's persisted data.

**Compose details:** `docker/compose.nifi.yml` pins `apache/nifi:2.12.0`, binds port to localhost only, and persists configuration, state, and flow/content/provenance repositories in named volumes. Docker Compose project/container name: `ai-incident-nifi`. If an earlier lab used the previous name `camel-etl-nifi`, those old volumes are **not automatically migrated**; do not remove old volumes until you've confirmed no data must be kept.

**Troubleshooting:** `make nifi-ps`, `make nifi-logs` and `docker logs ai-incident-nifi`. If you use a password under 12 characters, NiFi may generate different random credentials. Never paste secrets or unredacted credential-bearing startup logs into issues or chat.

Official reference: [Apache NiFi Docker image documentation](https://github.com/apache/nifi/blob/main/nifi-docker/dockerhub/README.md).

## PostgreSQL and pgAdmin (optional; later milestones)

Configuration is retained in `docker/compose.postgres.yml`. Before starting, set unique PostgreSQL and pgAdmin passwords in `.env`.

```sh
docker compose --env-file .env -f docker/compose.postgres.yml up -d
docker compose --env-file .env -f docker/compose.postgres.yml ps
docker compose --env-file .env -f docker/compose.postgres.yml down
```

pgAdmin is available at http://localhost:5050 (or `PGADMIN_PORT`). For a connection from pgAdmin, use hostname `postgres`, port `5432`, and the `POSTGRES_*` values. **Security caveat:** the retained Postgres Compose file publishes port 5432 on `0.0.0.0`; do not start it on an untrusted network without first restricting its binding. This service is not required for M0.

## Ollama and Open WebUI (optional)

Ollama runs on the host (not in a Compose file here); `docker/compose.webui.yml` defines the separate WebUI service. Run an installed local model with `make ollama` or `make ollama-gemma` / `make ollama-qwen`.

Open WebUI, if needed, can be started independently:

```sh
docker compose --env-file .env -f docker/compose.webui.yml up -d open-webui
```

Open http://localhost:3000. Configure a long random `WEBUI_SECRET_KEY` in `.env`. To reach host Ollama from Docker, the host API must be reachable from the container; `make ollama-serve` defaults to `127.0.0.1:11434` for safety and therefore may **not** be reachable from Open WebUI. Only change that bind setting after checking firewall/access restrictions. The WebUI Compose currently publishes port 3000 on all interfaces; restrict it before using an untrusted network. Neither service is necessary for M0.
