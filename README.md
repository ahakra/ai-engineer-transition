# AI Integration & Incident Analysis Platform

Portfolio project for evidence-grounded diagnosis of failures across integration systems. **Apache NiFi is the first adapter**, not the entire product.

**Current milestone: M0 — NiFi Lab.** No running NiFi instance or incident scenario has been verified yet.

## First local setup

1. Install Docker Engine with Compose v2, GNU Make, and curl.
2. Copy `.env.example` to `.env` and replace sample credentials, especially `NIFI_PASSWORD` (12+ characters).
3. Run `make nifi-config`, `make nifi-pull`, `make nifi-up`, then `make nifi-ps`.
4. Follow `make nifi-logs`. Visit https://localhost:8443/nifi/ (or the port configured in `.env`), wait for startup, and log in.
5. Verify that the HTTPS endpoint responds as described in [docker/README.md](docker/README.md). Stop with `make nifi-down`.

See [AGENTS.md](AGENTS.md) for engineering rules, [docs/ROADMAP.md](docs/ROADMAP.md) for milestones, and [docs/PROGRESS.md](docs/PROGRESS.md) for verifiable progress.

**Working agreement:** The repository owner implements changes; ChatGPT reviews code and verifies submitted evidence. No task is marked complete from configuration alone.
