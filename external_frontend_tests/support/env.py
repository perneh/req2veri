"""Frontend base URL — same precedence idea as ``external_tests/support/env.py`` for the API."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final

_DEFAULT_HOST: Final[str] = "127.0.0.1"
_DEFAULT_PORT: Final[str] = "5173"


def resolve_frontend_root(
    environ: Mapping[str, str] | None = None,
    *,
    cli_host: str | None = None,
    cli_port: str | None = None,
) -> str:
    """
    SPA origin for pytest-playwright (no path).

    Precedence:
    1. REQ2VERI_FRONTEND_BASE_URL — full origin, e.g. http://127.0.0.1:5173
    2. Else http://HOST:PORT from ``--host`` / ``--port`` when set, otherwise
       REQ2VERI_FRONTEND_HOST / REQ2VERI_FRONTEND_PORT (defaults: 127.0.0.1:5173).
    """
    env = dict(environ) if environ is not None else dict(os.environ)
    raw = (env.get("REQ2VERI_FRONTEND_BASE_URL") or "").strip()
    if raw:
        return raw.rstrip("/")
    host = cli_host if cli_host is not None else (env.get("REQ2VERI_FRONTEND_HOST") or _DEFAULT_HOST)
    host = str(host).strip() or _DEFAULT_HOST
    port = cli_port if cli_port is not None else (env.get("REQ2VERI_FRONTEND_PORT") or _DEFAULT_PORT)
    port = str(port).strip() or _DEFAULT_PORT
    return f"http://{host}:{port}".rstrip("/")
