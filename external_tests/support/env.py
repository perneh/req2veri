from collections.abc import Mapping
from typing import Final

_DEFAULT_HOST: Final[str] = "127.0.0.1"
_DEFAULT_PORT: Final[str] = "8000"


def resolve_api_root(
    *,
    cli_base_url: str | None = None,
    environ: Mapping[str, str] | None = None,
    host: str | None = None,
    port: str | None = None,
) -> str:
    """Pick API root: full CLI URL, then host/port if either CLI flag was set, else env, else defaults."""
    if cli_base_url:
        return str(cli_base_url).rstrip("/")
    if host is not None or port is not None:
        h = (host or _DEFAULT_HOST).strip() or _DEFAULT_HOST
        p = (port or _DEFAULT_PORT).strip() or _DEFAULT_PORT
        return f"http://{h}:{p}".rstrip("/")
    env = environ or {}
    if env.get("REQ2VERI_BASE_URL"):
        return str(env["REQ2VERI_BASE_URL"]).rstrip("/")
    return f"http://{_DEFAULT_HOST}:{_DEFAULT_PORT}".rstrip("/")


def base_url(environ: Mapping[str, str] | None = None) -> str:
    """Backward-compatible: env URL or default host:port."""
    return resolve_api_root(environ=environ)
