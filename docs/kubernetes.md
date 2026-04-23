# Run req2veri on Kubernetes

Short guide with **Helm** and notes for **Docker Desktop**.

## URLs and addresses (after install)

Values depend on how you expose the app. Pick the row that matches your setup.

### Option A: `kubectl port-forward` (ingress off)

After:

```bash
kubectl -n req2veri port-forward svc/frontend 8080:80
```

| What | URL or address |
|------|----------------|
| **Web UI** | http://localhost:8080/ |
| **API from the browser** (nginx in frontend pod) | http://localhost:8080/api/… (same host as the UI) |
| **Example health via UI proxy** | http://localhost:8080/api/health |
| **Swagger via UI proxy** | http://localhost:8080/api/docs |

Forward the **backend** directly (optional, second terminal):

```bash
kubectl -n req2veri port-forward svc/backend 8000:8000
```

| What | URL |
|------|-----|
| **Backend on your machine** | http://localhost:8000/ |
| **Swagger** | http://localhost:8000/docs |

### Option B: Ingress enabled (`ingress.host` you set, e.g. `req2veri.local`)

Add to `/etc/hosts` (example):

```text
127.0.0.1 req2veri.local
```

(Use your ingress IP if not local.)

| What | URL |
|------|-----|
| **Web UI** | http://req2veri.local/ (or `https://…` if TLS terminates at ingress) |
| **API from the browser** | http://req2veri.local/api/… |

### Inside the cluster (for debugging)

| Service | DNS name | Port |
|---------|----------|------|
| Frontend | `frontend.<namespace>.svc.cluster.local` | 80 |
| Backend | `backend.<namespace>.svc.cluster.local` | 8000 |
| Postgres | `postgres.<namespace>.svc.cluster.local` | 5432 |

Example (namespace `req2veri`): `http://backend.req2veri.svc.cluster.local:8000/health` from another pod.

---

## Prerequisites

- `kubectl` and `helm` installed
- A working cluster (see [Docker Desktop](#kubernetes-in-docker-desktop) below)
- Images the cluster can run (see [Build images](#build-images))

## Build images

From the **repository root**:

```bash
docker build -t req2veri-backend:latest ./backend
docker build -t req2veri-frontend:latest ./frontend
```

On **Docker Desktop**, the Kubernetes cluster uses the same image store as Docker Engine, so these tags are usually enough—no registry push required for local testing.

## Install with Helm

Pick a hostname you will use in `/etc/hosts` (example: `req2veri.local`). Install into namespace `req2veri`:

```bash
helm upgrade --install req2veri ./deploy/helm/req2veri \
  --namespace req2veri --create-namespace \
  --set secrets.postgresPassword="$(openssl rand -hex 16)" \
  --set secrets.jwtSecret="$(openssl rand -hex 32)" \
  --set ingress.host=req2veri.local
```

**Ingress:** the chart expects an **nginx** ingress class by default. If you do not have an ingress controller, disable ingress and use port-forward (simplest on a fresh Docker Desktop cluster):

```bash
helm upgrade --install req2veri ./deploy/helm/req2veri \
  --namespace req2veri --create-namespace \
  --set ingress.enabled=false \
  --set secrets.postgresPassword="$(openssl rand -hex 16)" \
  --set secrets.jwtSecret="$(openssl rand -hex 32)"
```

Then forward the frontend service:

```bash
kubectl -n req2veri port-forward svc/frontend 8080:80
```

Open **http://localhost:8080/** in the browser.

## Useful commands

```bash
kubectl -n req2veri get pods
kubectl -n req2veri logs deploy/backend --tail=100
```

Uninstall release:

```bash
helm uninstall req2veri -n req2veri
```

More chart details: [deploy/helm/README.md](../deploy/helm/README.md).

---

## Kubernetes in Docker Desktop

1. Open **Docker Desktop** → **Settings** (gear icon).
2. Go to **Kubernetes** in the left sidebar.
3. Enable **Kubernetes**, then click **Apply & Restart** and wait until the status shows Kubernetes is running.

### Point `kubectl` at Docker Desktop

```bash
kubectl config use-context docker-desktop
kubectl get nodes
```

You should see one ready node (often named `docker-desktop`).

### Why this is convenient

- One machine runs **Docker** and a **local Kubernetes** cluster.
- Images you build with `docker build ...` are typically **visible to that cluster**, so you can iterate without pushing to Docker Hub or another registry (ideal for this project’s Helm `values.yaml` image names like `req2veri-backend:latest`).

### Optional: ingress on Docker Desktop

If you want `Ingress` resources to work, install an ingress controller (for example the community **ingress-nginx** chart) and match `ingress.className` in `deploy/helm/req2veri/values.yaml` to your controller. Until then, use **`ingress.enabled=false`** and **`kubectl port-forward`** as above.

### Resource tip

Kubernetes in Docker Desktop shares CPU/RAM with Docker. If pods stay `Pending`, increase **Docker Desktop → Settings → Resources** (CPUs / Memory).
