"""Resolved SPA origin — single place for ``--host`` / ``--port`` and env (see ``support/env.py``)."""

from __future__ import annotations

import os
from urllib.parse import urlparse

from support.env import resolve_frontend_root


def resolve_frontend_target(cli_host: str | None, cli_port: str | None) -> str:
    """Origin passed to Playwright ``base_url``; mirrors pytest ``--host`` / ``--port``."""
    return resolve_frontend_root(os.environ, cli_host=cli_host, cli_port=cli_port)


def assert_origin_is_http(origin: str) -> None:
    assert origin.startswith("http://") or origin.startswith("https://"), (
        f"expected absolute origin, got {origin!r}"
    )


def assert_origin_host(origin: str, expected_host: str) -> None:
    host = urlparse(origin).hostname
    assert host == expected_host, f"origin {origin!r}: host {host!r} != {expected_host!r}"


def assert_origin_port(origin: str, expected_port: int) -> None:
    port = urlparse(origin).port
    assert port == expected_port, f"origin {origin!r}: port {port!r} != {expected_port!r}"
