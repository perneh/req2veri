# Run req2veri with Docker Compose

From the **repository root** (where `docker-compose.yml` is).

## URLs and addresses (copy-paste)

| What | URL or address |
|------|----------------|
| **Web UI** | http://localhost:5173/ |
| **Backend REST** (from your machine) | http://localhost:8000/ |
| **Health** | http://localhost:8000/health |
| **OpenAPI (Swagger UI)** | http://localhost:8000/docs |
| **Swagger via Vite proxy** (same tab as UI) | http://localhost:5173/api/docs |
| **Alternative OpenAPI** | http://localhost:8000/redoc |
| **API via same origin as UI** (browser) | http://localhost:5173/api/… (Vite proxies to the backend) |
| **PostgreSQL** (host → container) | `localhost:5432` — DB `req2veri`, user `req2veri`, password `req2veri` |
| **Database URL** (inside Compose network) | `postgresql+psycopg2://req2veri:req2veri@db:5432/req2veri` |

Example API call from the host:

```bash
curl -s http://localhost:8000/health
```

## Start everything

```bash
docker compose up --build
```

Wait until the database is healthy, the backend has run migrations and seed, and the frontend dev server is up.

The dev frontend proxies `/api` to **`http://host.docker.internal:8000`** (the backend port published on your machine), not the hostname `backend`, so the Vite container does not depend on Docker’s internal service DNS (which can otherwise cause `getaddrinfo ENOTFOUND backend`).

## Open the app

Browser: **http://localhost:5173/**

Optional: **http://localhost:8000/docs** to try the API interactively.

## Demo login

After the first successful start, the seed creates a user:

- **Username:** `demo`  
- **Password:** `demo12345`

## Stop

Press `Ctrl+C` in the terminal, or in another shell:

```bash
docker compose down
```

To also remove the Postgres volume (wipes data):

```bash
docker compose down -v
```

## Reset to an empty database (then start again)

Removes the Postgres volume so the next start is a **fresh** database (migrations + seed run again from scratch):

```bash
docker compose down -v
docker compose up --build
```

This deletes **all** stored data (requirements, users, tests, etc.). The demo user `demo` / `demo12345` is recreated by the seed script after `up`.

## Ports (same info as URLs)

| Service    | Host port | Example URL |
|------------|-----------|-------------|
| Frontend   | 5173      | http://localhost:5173/ |
| Backend    | 8000      | http://localhost:8000/ |
| Postgres   | 5432      | `postgresql://req2veri:req2veri@127.0.0.1:5432/req2veri` |

If something else already uses these ports, edit `docker-compose.yml` or stop the conflicting service.
