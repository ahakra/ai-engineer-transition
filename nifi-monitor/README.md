# NiFi Monitor — M1 Python Monitoring

Read-only Apache NiFi monitoring CLI for the AI Integration & Incident Analysis Platform.

## Setup

From the repository root:

```sh
cd nifi-monitor
uv sync
cp .env.example .env
```

Edit `.env` with your local NiFi URL, original Process Group ID and valid NiFi username/password. **Never commit `.env` or credentials.** `.env.example` is an example, not a credential store.

```sh
uv run nifi-monitor
```

The CLI authenticates with NiFi, lists processors in the configured process group and shows the `ValidateJson` runtime status in readable tables. Its operational API requests are GET-only. The authentication token is obtained using POST and is not printed.

### Python commands (from `nifi-monitor/`)

| Command | What it does | Changes files? |
| --- | --- | --- |
| `uv sync` | Synchronizes `.venv` with `pyproject.toml` and `uv.lock` | Environment only |
| `uv run nifi-monitor` | Runs the CLI against your configured NiFi instance | No NiFi changes |
| `uv run ruff check .` | Finds lint errors: unused imports, bug-prone constructs, import ordering, etc. | No |
| `uv run ruff format --check .` | Reports files that are not formatted as Ruff expects | No |
| `uv run ruff format .` | Applies Python formatting automatically | **Yes: source files** |
| `uv run mypy src` | Checks type annotations without running the application | No |
| `uv run pytest -v` | Runs tests with verbose test names/results | No NiFi changes; pytest may write caches |
| `uv run ruff check --fix .` | Automatically applies supported lint fixes | **Yes: source files** |

### Make commands (from repository root)

The root `Makefile` runs the same commands from `nifi-monitor/`, so you do not have to change directories.

| Command | Equivalent | Purpose |
| --- | --- | --- |
| `make monitor-run` | `uv run nifi-monitor` | Run NiFi monitor CLI |
| `make monitor-lint` | `uv run ruff check .` | Lint |
| `make monitor-format-check` | `uv run ruff format --check .` | Check formatting |
| `make monitor-format` | `uv run ruff format .` | **Rewrite formatting** |
| `make monitor-typecheck` | `uv run mypy src` | Static type checking |
| `make monitor-test` | `uv run pytest -v` | Run offline tests |
| `make monitor-check` | lint + format-check + typecheck + tests | One command for quality checks |

Quality gate before every push:

```sh
make monitor-check
```

The checks stop on the first failing command. `monitor-check` does **not** auto-fix source code. Run `make monitor-format` separately when formatting is needed, then rerun `make monitor-check`.

## Code organization

- `src/nifi_monitor/main.py`: CLI entry point, configuration loading and terminal tables.
- `src/nifi_monitor/nifi_client.py`: HTTPX authentication and NiFi API access.
- `tests/test_monitor.py`: offline tests using HTTPX MockTransport and output assertions.

### Python concepts demonstrated

- `str | None` means a value is either a string or absent. Prefer this over initializing `""` when a variable later holds a processor ID.
- `Sequence[tuple[str, ...]]` is appropriate for read-only table rows; it accepts specific tuple lengths, unlike an invariant `list` annotation.
- `zip(..., strict=True)` raises when input lengths differ rather than silently dropping values.
- `typing.cast(...)` tells the type checker what a JSON object should contain **without validating it at runtime**. Real response schema validation is future work.
- Missing metrics display `N/A`, not `0`, because missing evidence is not evidence of zero activity.

## Current limitations

- Local NiFi uses a self-signed certificate; `verify=False` is **not production-safe**. Trust a CA certificate for secure deployments.
- The demo username has whatever NiFi permissions it was granted; the CLI deliberately avoids write-capable operational endpoints, but authentication is not a read-only permission boundary.
- NiFi status metrics are reporting-window values, not lifetime counters.
- Remote JSON is only partially typed and is not yet validated against a schema.
