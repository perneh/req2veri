import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import Settings


def setup_file_logging(settings: Settings) -> None:
    """Enable file-based logging for the application process."""
    log_path = Path(settings.app_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    level = getattr(logging, settings.app_log_level.upper(), logging.INFO)
    root.setLevel(level)

    abs_target = str(log_path.resolve())
    for h in root.handlers:
        if isinstance(h, RotatingFileHandler) and Path(h.baseFilename).resolve() == log_path.resolve():
            return

    handler = RotatingFileHandler(
        filename=abs_target,
        maxBytes=settings.app_log_max_bytes,
        backupCount=settings.app_log_backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root.addHandler(handler)
