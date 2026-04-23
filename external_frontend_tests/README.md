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
