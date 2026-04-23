# req2veri Helm chart

Chart path: `deploy/helm/req2veri`.

## URLs after install (depends on exposure)

| How you reach the app | Web UI | API from browser |
|----------------------|--------|------------------|
| **Port-forward** `svc/frontend 8080:80` | http://localhost:8080/ | http://localhost:8080/api/… (Swagger: http://localhost:8080/api/docs) |
| **Ingress** host `req2veri.local` (example) | http://req2veri.local/ | http://req2veri.local/api/… |
| **Port-forward backend** `svc/backend 8000:8000` | — | http://localhost:8000/ and http://localhost:8000/docs |

Cluster-internal (from a pod): `http://frontend.<namespace>.svc.cluster.local/`, `http://backend.<namespace>.svc.cluster.local:8000/`.

## What it deploys

- All resources are created in the **Helm release namespace** (use `-n req2veri --create-namespace` in the example below).
- PostgreSQL `StatefulSet` with a `PersistentVolumeClaim`
- Backend `Deployment` (init container runs `alembic upgrade head`)
- Frontend `Deployment` (nginx static assets + reverse proxy of `/api/` to the backend service)
- Services for `postgres`, `backend`, and `frontend`
- Optional `Ingress` exposing the frontend (port 80); API traffic uses the same host under `/api/`

## Prerequisites

- Kubernetes cluster (small clusters are fine; defaults use one replica and modest CPU/memory limits)
- Ingress controller if you enable ingress (values assume **nginx** ingress class)
- Container images built and available to the cluster (`backend.image`, `frontend.image`)

## Install

```bash
helm upgrade --install req2veri ./deploy/helm/req2veri \
  --namespace req2veri --create-namespace \
  --set secrets.postgresPassword="$(openssl rand -hex 16)" \
  --set secrets.jwtSecret="$(openssl rand -hex 32)" \
  --set ingress.host=req2veri.example.com
```

Tune `values.yaml` for image names, resource limits, storage size, and ingress host.

## Notes

- Set `ingress.enabled` to `false` if you expose services via `kubectl port-forward` or another ingress.
- After first install, register a user via `POST /api/auth/register` or extend the chart with a bootstrap `Job` if you need automated seeding in the cluster.
