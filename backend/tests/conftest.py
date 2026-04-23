import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///./test_req2veri.db",
)
os.environ.setdefault("RESET_DB_USER", "reset-admin")
os.environ.setdefault("RESET_DB_PASSWORD", "reset-test-password")
os.environ.setdefault("BACKUP_DIR", tempfile.mkdtemp(prefix="req2veri_backup_"))

from app.database import get_session  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    app = create_app()

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as c:
        yield c
