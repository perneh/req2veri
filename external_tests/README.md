# External backend tests

Black-box checks against a running API (cluster, port-forward, or local `uvicorn`). Uses **pytest** and **httpx** from a **venv on the host**.

## Setup

```bash
cd external_tests
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration (API target — environment only)

Switch **which backend** the suite talks to by exporting variables before `pytest` (no custom URL flags on the pytest command).

| Variable | Role |
|----------|------|
| **`REQ2VERI_BASE_URL`** | If set, full API root (scheme + host + optional port + path). Example: `http://127.0.0.1:8000` or `https://staging.example.com/api`. Trailing slash is stripped. |
| **`REQ2VERI_API_HOST`** | Used only when `REQ2VERI_BASE_URL` is unset. Default: `127.0.0.1` |
| **`REQ2VERI_API_PORT`** | Used only when `REQ2VERI_BASE_URL` is unset. Default: `8000` |

Effective URL when `REQ2VERI_BASE_URL` is unset: `http://{REQ2VERI_API_HOST}:{REQ2VERI_API_PORT}`.

Examples:

```bash
export REQ2VERI_BASE_URL=http://my-cluster.local:8080
pytest suite_10_functional

export REQ2VERI_API_HOST=192.168.1.50 REQ2VERI_API_PORT=9000
pytest
```

## Suites (order)

| Order | Directory | Role |
|------|-------------|------|
| 1 | `suite_00_empty/` | Expects **no** requirements, sub-requirements, or tests in the DB (see below). |
| 2 | `suite_10_functional/` | One module per **endpoint group** (auth, users, requirements, subrequirements, tests, dashboard, versions). |
| 3 | `suite_99_load/` | Bulk tree: **500** requirements × **10** sub-requirements × **2** tests per sub (marker `@load`). Also **version/run trends**: several `test-object-versions`, multiple verification tests, and one `POST …/runs` per (version, test) with varied statuses so per-version and per-test outcomes differ (asserted via `GET …/runs`). |

In the load suite, test-case creation is distributed round-robin across **10 different users**.

**Empty-system suite:** `GET /dashboard/summary` must report zero totals. Use a **fresh/empty database** (no seed data) for a full green run, or run only this folder when the instance is clean:

`pytest suite_00_empty`

After functional or load tests, totals are no longer zero — re-run suite 00 only after wiping data or on a dedicated empty instance.

Optional convenience: if either `REQ2VERI_RESET_DB_USER` + `REQ2VERI_RESET_DB_PASSWORD` (or fallback `RESET_DB_USER` + `RESET_DB_PASSWORD`) is set in the environment, `suite_00_empty` calls `POST /admin/reset-database` when non-zero totals are detected. If backend reset is disabled (`503`) or no reset credentials are provided, the suite falls back to deleting requirements/tests via normal APIs before asserting zero totals.

## Run

```bash
# Default target: http://127.0.0.1:8000 (override with REQ2VERI_BASE_URL or HOST/PORT — see above)
pytest
# Skip the heavy load test (~15k HTTP requests by default):
pytest -m "not load"
# Only the bulk scenario:
pytest -m load
```

### Run a specific suite (with examples)

```bash
# Empty-system suite only
pytest suite_00_empty

# Functional endpoint-group suites only
pytest suite_10_functional

# One endpoint group only (example: tests endpoints)
pytest suite_10_functional/test_tests_endpoints.py

# Load suite only
pytest suite_99_load -m load
```

### Progress and statistics

Use these common flags when you want better runtime feedback:

```bash
# Show each test and progress while running
pytest -v

# Print durations for the slowest tests
pytest --durations=10

# More detailed summary for skipped/failed/xfailed, etc.
pytest -ra

# Typical "watch" command for CI-like output
pytest -v -ra --durations=10
```

### Stop quickly on failures

```bash
# Stop after first failing test
pytest -x

# Stop after N failures
pytest --maxfail=3

# Combine with suite selection
pytest suite_10_functional -x -v
```

### Bulk scale (environment)

| Variable | Default |
|----------|---------|
| `REQ2VERI_LOAD_REQS` | `500` |
| `REQ2VERI_LOAD_SUBS_PER_REQ` | `10` |
| `REQ2VERI_LOAD_TESTS_PER_SUB` | `2` |
| `REQ2VERI_LOAD_TREND_VERSIONS` | `4` (test-object versions in `test_version_run_trends`) |
| `REQ2VERI_LOAD_TREND_TESTS` | `3` (verification tests, each with one run per version) |

Example smoke with smaller tree: `REQ2VERI_LOAD_REQS=2 REQ2VERI_LOAD_SUBS_PER_REQ=3 pytest -m load`.

Smaller version-trend only: `REQ2VERI_LOAD_TREND_VERSIONS=2 REQ2VERI_LOAD_TREND_TESTS=2 pytest suite_99_load/test_version_run_trends.py -m load`.

Helpers live under `support/`; tests stay thin.
