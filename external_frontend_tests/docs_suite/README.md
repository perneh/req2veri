# User manual generator (Playwright + Markdown)

This folder is a **pytest** suite that drives the live SPA, captures **screenshots**, and writes a small **user manual** as Markdown (`output/index.md` plus one file per chapter).

## What you get

- **Why** — short rationale for each screen (traceability, reporting, etc.)
- **How** — which nav control to use (English UI, same labels as `frontend` i18n)
- **Screenshot** — full-page PNG under `output/images/`

## Prerequisites

Same as the main [external frontend tests README](../README.md): Vite (or preview) on the same port as pytest, backend API reachable, seeded `demo` / `demo12345` user unless you set `REQ2VERI_E2E_USERNAME` / `REQ2VERI_E2E_PASSWORD`.

## Run

```bash
cd external_frontend_tests
source .venv/bin/activate
# Terminal A: frontend
cd ../frontend && npm run dev
# Terminal B: generate manual (port must match the SPA, default 5173)
cd ../external_frontend_tests
pytest docs_suite/tests/ -v --port 5173
```

Optional: set output directory (absolute or relative to cwd):

```bash
REQ2VERI_MANUAL_OUTPUT=./my-manual pytest docs_suite/tests/ -v --port 5173
```

## Output

Default: `docs_suite/output/`

- `index.md` — table of contents linking all chapters
- `*.md` — one chapter per topic
- `images/*.png` — screenshots

Git: `external_frontend_tests/.gitignore` allows committing **`output/index.md`**, **`output/*.md`**, and **`output/images/**/*.png`**. Other stray files under `output/` stay ignored. You can also copy PNGs into root **`docs/images/`** for the main docs (see `docs/images/.gitignore`).

## CI

Omitted from the default `pytest` `testpaths` so normal runs stay fast. Run this suite explicitly when you want refreshed documentation, or in a separate scheduled job.
