from hmac import compare_digest

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import SQLModel

from app.config import get_settings
from app.database import get_engine

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()

@router.post("/reset-database")
def reset_database(
    creds: Annotated[HTTPBasicCredentials, Depends(security)],
):
    settings = get_settings()
    configured_user = settings.reset_db_user
    configured_password = settings.reset_db_password
    if not configured_user or not configured_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database reset endpoint is disabled",
        )
    if not (
        compare_digest(creds.username, configured_user)
        and compare_digest(creds.password, configured_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    engine = get_engine()
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    return {"ok": True}
