from collections import deque
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, dashboard, requirements, subrequirements, test_versions, tests, users
from app.config import get_settings
from app.logging_config import setup_file_logging


def create_app() -> FastAPI:
    settings = get_settings()
    setup_file_logging(settings)
    app = FastAPI(title="req2veri API", version="0.1.0")

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(requirements.router)
    app.include_router(subrequirements.router)
    app.include_router(tests.router)
    app.include_router(dashboard.router)
    app.include_router(test_versions.router)
    app.include_router(admin.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/logs")
    def logs(lines: int = Query(200, ge=1, le=200)):
        path = Path(settings.app_log_file)
        if not path.exists():
            return {"path": str(path), "lines": []}
        with path.open("r", encoding="utf-8", errors="replace") as f:
            tail = deque(f, maxlen=lines)
        return {"path": str(path), "lines": [x.rstrip("\n") for x in tail]}

    return app


app = create_app()
