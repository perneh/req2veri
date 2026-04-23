# req2veri

Web app for requirements, sub-requirements, and verification tests (traceability, coverage, CI-style test runs per version).

## URLs at a glance (default ports)

| Setup | App (browser) | API (direct) | API docs |
|--------|---------------|--------------|----------|
| **Docker Compose** | http://localhost:5173/ | http://localhost:8000/ | http://localhost:8000/docs or http://localhost:5173/api/docs |
| **Kubernetes** (port-forward to 8080) | http://localhost:8080/ | Same host: http://localhost:8080/api/… | http://localhost:8080/api/docs (via frontend nginx → backend) |

Details and more examples: [docs/docker-compose.md](docs/docker-compose.md), [docs/kubernetes.md](docs/kubernetes.md).

## Quick start

| How you want to run it | Guide |
|------------------------|--------|
| **Docker Compose** (simplest) | [docs/docker-compose.md](docs/docker-compose.md) |
| **Kubernetes** (Helm) + **Docker Desktop** | [docs/kubernetes.md](docs/kubernetes.md) |

## More docs

| Topic | Link |
|--------|------|
| Backend (API, env, migrations, seed) | [backend/README.md](backend/README.md) |
| Frontend (dev, build, i18n) | [frontend/README.md](frontend/README.md) |
| **Using the web UI** (login, pages, language) | [frontend/HOWTO.md](frontend/HOWTO.md) |
| Helm chart details | [deploy/helm/README.md](deploy/helm/README.md) |

## Tests (without Docker)

```bash
cd backend && PYTHONPATH=. pytest tests/
cd frontend && npm test
```

**External (black-box) API checks** from the host: [external_tests/README.md](external_tests/README.md) — ordered suites (empty DB → per-endpoint groups → optional `@load` bulk tree), `venv`, `httpx`, `pytest`. Point tests at another API with **`REQ2VERI_BASE_URL`** or **`REQ2VERI_API_HOST`** / **`REQ2VERI_API_PORT`** (no pytest URL flags).

For local Postgres + `uvicorn` / `npm run dev`, see the backend and frontend READMEs above.

## Images

Screenshots and diagrams: [docs/images](docs/images)
