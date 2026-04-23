# req2veri backend

FastAPI service with layered modules: `api/routes`, `services`, `repositories`, `models`, and `schemas`.

## Configuration

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg2://req2veri:req2veri@localhost:5432/req2veri` |
| `CORS_ORIGINS` | Comma-separated browser origins (e.g. `http://localhost:5173,http://127.0.0.1:5173`) |
| `JWT_SECRET_KEY` | Symmetric key for access tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 1440) |
| `RESET_DB_USER` | Basic-auth username for `POST /admin/reset-database` (dev/test only) |
| `RESET_DB_PASSWORD` | Basic-auth password for `POST /admin/reset-database` (dev/test only) |
| `APP_LOG_FILE` | File path for backend logs (default `logs/app.log`) |
| `APP_LOG_LEVEL` | Log level for file logging (default `INFO`) |
| `APP_LOG_MAX_BYTES` | Rotate log file when larger than this many bytes (default `5242880`) |
| `APP_LOG_BACKUP_COUNT` | Number of rotated log files to keep (default `5`) |

## URLs (default local dev)

With `uvicorn` on port **8000** (see [Local development](#local-development)):

| Page / use | URL |
|------------|-----|
| API base | http://127.0.0.1:8000/ |
| Health | http://127.0.0.1:8000/health |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Example list requirements | http://127.0.0.1:8000/requirements (needs `Authorization: Bearer …`) |

Same with `localhost`: http://localhost:8000/docs

## Local development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://req2veri:req2veri@localhost:5432/req2veri
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Migrations

```bash
export DATABASE_URL=...
alembic revision --autogenerate -m "message"   # when models change
alembic upgrade head
```

## API overview

Public health check: `GET /health`.

All JSON APIs except registration and token exchange require `Authorization: Bearer <token>`.
Requirement, sub-requirement, and verification-test read payloads include `updated_at` and `updated_by`.

| Area | Paths |
|------|--------|
| Auth | `POST /auth/register`, `POST /auth/token` (OAuth2 password form) |
| Users | `GET /users` (list registered users), `GET /users/me` |
| Requirements | `GET/POST /requirements`, `GET /requirements/hierarchy` (all reqs + sub-reqs), `GET/PATCH/DELETE /requirements/{id}` |
| Sub-requirements | `GET/POST /requirements/{id}/subrequirements`, `GET/PATCH/DELETE /subrequirements/{id}` |
| Tests | `GET/POST /tests` (body includes `precondition`, `action`, optional requirement links; `status` / `actual_result` default for new tests), `GET /tests?reference=` `any` / `linked` / `unlinked`, `GET/PATCH/DELETE /tests/{id}`, `GET/POST /requirements/{id}/tests`, `GET/POST /subrequirements/{id}/tests` |
| Coverage / trace | `GET /requirements/{id}/coverage`, `GET /requirements/{id}/traceability` |
| Dashboard | `GET /dashboard/summary` |
| CI versions | `GET/POST /test-object-versions`, `GET/POST /test-object-versions/{id}/runs` |
| Admin | `POST /admin/reset-database` (HTTP Basic auth with `RESET_DB_USER` / `RESET_DB_PASSWORD`; resets all tables) |

## Tests

```bash
cd backend
source .venv/bin/activate
pip install pytest
PYTHONPATH=. pytest
```
