import os
from collections.abc import Mapping
from typing import Final

_DEFAULT_HOST: Final[str] = "127.0.0.1"
_DEFAULT_PORT: Final[str] = "8000"


def resolve_api_root(environ: Mapping[str, str] | None = None) -> str:
    """
    API base URL for all external_tests — environment only (no pytest CLI flags).

    Precedence:
    1. REQ2VERI_BASE_URL — full base URL, e.g. https://api.example.com or http://127.0.0.1:8000
    2. Else http://REQ2VERI_API_HOST:REQ2VERI_API_PORT (defaults: 127.0.0.1:8000)
    """
    env = dict(environ) if environ is not None else dict(os.environ)
    raw = (env.get("REQ2VERI_BASE_URL") or "").strip()
    if raw:
        return raw.rstrip("/")
    host = (env.get("REQ2VERI_API_HOST") or _DEFAULT_HOST).strip() or _DEFAULT_HOST
    port = (env.get("REQ2VERI_API_PORT") or _DEFAULT_PORT).strip() or _DEFAULT_PORT
    return f"http://{host}:{port}".rstrip("/")


def base_url(environ: Mapping[str, str] | None = None) -> str:
    """Same as resolve_api_root; kept for callers that only need env-based URL."""
    return resolve_api_root(environ=environ)
