from hmac import compare_digest

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import SQLModel

from app.config import get_settings
from app.database import get_engine
from app.services.database_backup import delete_database_backup, run_database_backup

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()


def _verify_reset_admin_credentials(creds: HTTPBasicCredentials) -> None:
    settings = get_settings()
    configured_user = settings.reset_db_user
    configured_password = settings.reset_db_password
    if not configured_user or not configured_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin database endpoints are disabled (missing RESET_DB_USER / RESET_DB_PASSWORD)",
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


@router.post("/reset-database")
def reset_database(
    creds: Annotated[HTTPBasicCredentials, Depends(security)],
):
    _verify_reset_admin_credentials(creds)
    engine = get_engine()
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    return {"ok": True}


@router.post("/backup-database")
def backup_database(
    creds: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Write a backup file under BACKUP_DIR (default ./backups). Same HTTP Basic auth as reset-database."""
    _verify_reset_admin_credentials(creds)
    settings = get_settings()
    return run_database_backup(database_url=settings.database_url, backup_dir=settings.backup_dir)


@router.delete("/backups/{filename}", status_code=204)
def delete_backup(
    creds: Annotated[HTTPBasicCredentials, Depends(security)],
    filename: str,
) -> None:
    """Remove one backup file from BACKUP_DIR (basename only; same auth as reset-database)."""
    _verify_reset_admin_credentials(creds)
    settings = get_settings()
    delete_database_backup(backup_dir=settings.backup_dir, filename=filename)
