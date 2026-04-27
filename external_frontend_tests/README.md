# External frontend tests (pytest + Playwright)

Black-box **browser** checks against a running SPA (Vite dev or preview). Tests are **Python** files using **pytest** and **pytest-playwright** (Chromium by default).

## Prerequisites

- **Frontend must already be running** on the URL you pass to pytest (default `http://127.0.0.1:5173`). If you use `--port 4173`, start Vite **preview** (or dev) on that port first — otherwise you get `ERR_CONNECTION_REFUSED`.
- Backend API reachable from the browser (same as manual use).
- Seeded or existing **`demo` / `demo12345`** user (or set credentials env vars below).
- At least one verification test for `tests/test_test_detail_e2e.py`.

## Setup

Use a **dedicated venv** in this directory so `pytest` is the same interpreter that has Playwright installed:

```bash
cd external_frontend_tests
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Run **`pytest` only after** `source .venv/bin/activate`. If you run the global `pytest` without installing here, you get `ModuleNotFoundError: No module named 'playwright'`.

## Troubleshooting

| Error | Fix |
|--------|-----|
| `ModuleNotFoundError: No module named 'playwright'` | `source .venv/bin/activate` then `pip install -r requirements.txt` (see Setup). |
| Browser missing | `playwright install chromium` |
| `ERR_CONNECTION_REFUSED` / “No HTTP server at …” | Start the UI on that host/port (`npm run dev` is usually **5173**; `npm run preview` is often **4173**). Match pytest: e.g. `pytest --port 5173` while `npm run dev` runs. If you use **`--port 4173`** but only ran **`npm run dev`**, nothing listens on 4173 — either start preview on 4173 or drop `--port` / use `--port 5173`. |
| Skip the startup HTTP probe | `pytest --allow-offline` or `REQ2VERI_E2E_ALLOW_OFFLINE=1` (tests still fail if the browser cannot connect). |
| Where are failure screenshots? | With the default `pytest.ini`, under **`test-results/`** after a failed test (`--screenshot only-on-failure`). |
| pip “new release available” notice | Optional: `export PIP_DISABLE_PIP_VERSION_CHECK=1` before `pip install`. |

## Configuration

Target URL uses the same precedence pattern as [external_tests](../external_tests/README.md) for the API: full base URL wins, otherwise host and port from **pytest** ``--host`` / ``--port`` and/or env.

| Source | Role |
|--------|------|
| **`REQ2VERI_FRONTEND_BASE_URL`** | If set, full SPA origin (no path), e.g. `http://127.0.0.1:5173`. Trailing slash is stripped. **When set, ``--host`` / ``--port`` are ignored.** |
| **`pytest --host HOST`** | Used only when `REQ2VERI_FRONTEND_BASE_URL` is unset. Overrides `REQ2VERI_FRONTEND_HOST`. Default host: `127.0.0.1` |
| **`pytest --port PORT`** | Used only when `REQ2VERI_FRONTEND_BASE_URL` is unset. Overrides `REQ2VERI_FRONTEND_PORT`. Default port: `5173` |
| **`REQ2VERI_FRONTEND_HOST`** | Used when the full frontend base URL is unset and ``--host`` is not passed. |
| **`REQ2VERI_FRONTEND_PORT`** | Used when the full frontend base URL is unset and ``--port`` is not passed. |
| **`REQ2VERI_E2E_USERNAME`** | Login username. Default: `demo`. |
| **`REQ2VERI_E2E_PASSWORD`** | Login password. Default: `demo12345`. |

At startup, the resolved origin is written to **`PYTEST_BASE_URL`** for pytest-playwright.

## Failure screenshots (Playwright)

Default runner options (see `pytest.ini`) include:

- **`--screenshot only-on-failure`** — when a test fails, Playwright saves a **PNG** (and related metadata) under the artifacts directory.
- **`--output test-results`** — artifact root (override with `pytest --output your/dir`).
- **`--full-page-screenshot`** — on failure, capture the **full scrollable page**, not only the viewport (requires the screenshot feature above).

After a failed run, look under **`test-results/`**. In addition to pytest-playwright artifacts, we also save a guaranteed fallback screenshot in:

- `test-results/manual-failure-screenshots/*.png`

This directory is listed in `.gitignore`.

## Intentional-failure suite (demo)

The folder **`screen_fail_suites/`** contains tests that are **meant to fail** so you can confirm screenshots and other failure artifacts. They are **not** part of the default `testpaths` (`tests/` only), so a normal `pytest` run stays green (assuming the app and passing tests are OK).

```bash
cd external_frontend_tests
source .venv/bin/activate
pytest screen_fail_suites/
```

You should see **failed** tests and new files under `test-results/`. Do not wire this path into a “must be green” CI job.

## Run

Terminal A (SPA):

```bash
cd frontend
npm run dev
# or preview on 4173:
# npm run preview -- --host 127.0.0.1 --port 4173
```

Terminal B (tests — **same port** as the UI):

```bash
cd external_frontend_tests
source .venv/bin/activate
pytest
pytest --host 127.0.0.1 --port 4173
# headed debugging:
pytest --headed --slowmo 500
```

**Collection:** a plain `pytest` only runs tests under **`tests/`** (see `pytest.ini` `testpaths`). To run the intentional failure package, use `pytest screen_fail_suites/` (see *Intentional-failure suite* above).

## Screenshot user manual (documentation)

The **`docs_suite/`** package runs Playwright, captures full-page images, and writes Markdown chapters plus `output/index.md` (why + how for each main screen). **Not** in default `testpaths` — run explicitly when you want to refresh the manual:

```bash
cd external_frontend_tests
source .venv/bin/activate
pytest docs_suite/tests/ -v --port 5173
```

See [docs_suite/README.md](docs_suite/README.md) for `REQ2VERI_MANUAL_OUTPUT` and details.
