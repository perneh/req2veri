# req2veri frontend

React SPA using Vite, MUI, TanStack Query, and `react-i18next` with **English**, **Swedish**, and **German** resources under `src/i18n/locales`.

## URLs (local dev)

| What | URL |
|------|-----|
| Dev server (after `npm run dev`) | http://localhost:5173/ |
| API calls from the browser | Uses `VITE_API_BASE` (default `/api`) → full paths like http://localhost:5173/api/requirements |
| Backend target for the Vite proxy | Default `http://127.0.0.1:8000` (`VITE_API_PROXY_TARGET`); with Docker Compose: `http://backend:8000` |

## Development

```bash
cd frontend
npm install
npm run dev
```

By default `VITE_API_BASE=/api` (see `.env.development`). The Vite dev server proxies `/api` to `VITE_API_PROXY_TARGET` (defaults to `http://127.0.0.1:8000`). With Docker Compose, `VITE_API_PROXY_TARGET` is set to `http://backend:8000`.

## Production build

```bash
npm run build
```

The production `Dockerfile` serves the app with nginx. Nginx forwards `/api/*` to the backend service (`http://backend:8000/`) so the browser can call `/api/...` on the same origin (used in the Helm deployment).

Override the API prefix at build time:

```bash
docker build --build-arg VITE_API_BASE=/api -t req2veri-frontend .
```

## UI tests

```bash
npm test
```
