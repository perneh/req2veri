from fastapi import FastAPI
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

    return app


app = create_app()
