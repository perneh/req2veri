"""Create on-disk database backups (SQLite file copy or PostgreSQL pg_dump)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.engine.url import make_url

# Filenames produced by run_database_backup only (prevents path tricks / deleting unrelated files).
_BACKUP_NAME_RE = re.compile(r"^req2veri_(sqlite|pg)_[0-9]{8}_[0-9]{6}\.(db|sql)$")


def _backup_root(backup_dir: str) -> Path:
    root = Path(backup_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_database_backup(*, database_url: str, backup_dir: str) -> dict:
    """
    Returns a dict: ok, path (absolute), format, bytes.
    Raises HTTPException on failure.
    """
    root = _backup_root(backup_dir)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    url = make_url(database_url)
    driver = url.drivername

    if driver.startswith("sqlite"):
        dbname = url.database
        if not dbname or dbname == ":memory:":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot backup in-memory or empty SQLite database",
            )
        src = Path(dbname)
        if not src.is_absolute():
            src = (Path.cwd() / src).resolve()
        if not src.is_file():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SQLite database file not found",
            )
        dest = root / f"req2veri_sqlite_{ts}.db"
        shutil.copy2(src, dest)
        size = dest.stat().st_size
        return {"ok": True, "path": str(dest), "format": "sqlite_copy", "bytes": size}

    if driver.startswith("postgresql"):
        host = url.host or "localhost"
        port = url.port or 5432
        user = url.username or ""
        password = url.password or ""
        db = url.database or ""
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PostgreSQL database name missing from URL",
            )
        dest = root / f"req2veri_pg_{ts}.sql"
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        cmd = [
            "pg_dump",
            "-h",
            host,
            "-p",
            str(port),
            "-U",
            user,
            "-d",
            db,
            "-f",
            str(dest),
            "--no-owner",
            "--no-acl",
        ]
        try:
            proc = subprocess.run(
                cmd,
                check=False,
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="pg_dump not found; install PostgreSQL client tools for backups",
            ) from None
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip() or f"exit {proc.returncode}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"pg_dump failed: {err[:2000]}",
            )
        size = dest.stat().st_size
        return {"ok": True, "path": str(dest), "format": "postgresql_sql", "bytes": size}

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Backup not implemented for database driver: {driver}",
    )


def _backup_file_path(*, backup_dir: str, filename: str) -> Path:
    name = Path(filename).name
    if name != filename or "/" in filename or "\\" in filename or filename in (".", ".."):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid backup filename")
    if not _BACKUP_NAME_RE.match(name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid backup filename")
    root = _backup_root(backup_dir).resolve()
    target = (root / name).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found") from None
    if not target.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    return target


def delete_database_backup(*, backup_dir: str, filename: str) -> None:
    path = _backup_file_path(backup_dir=backup_dir, filename=filename)
    path.unlink()
