"""Registration and token exchange; side effects only through httpx."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import Any, Final

import httpx

from support import http

_MIN_PASSWORD_LEN: Final[int] = 8


def unique_username(*, prefix: str = "ext") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def register_payload(*, username: str, password: str, email: str | None = None) -> dict[str, Any]:
    if len(password) < _MIN_PASSWORD_LEN:
        raise ValueError("password too short for API")
    return {
        "username": username,
        "email": email or f"{username}@example.com",
        "password": password,
    }


def bearer_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def merge_headers(*parts: Mapping[str, str] | None) -> dict[str, str]:
    return {k: v for m in parts if m for k, v in m.items()}


def register(client: httpx.Client, payload: Mapping[str, Any]) -> httpx.Response:
    return http.post_json(client, "/auth/register", dict(payload))


def token(client: httpx.Client, *, username: str, password: str) -> httpx.Response:
    return http.post_form(client, "/auth/token", {"username": username, "password": password})


def access_token(response: httpx.Response) -> str:
    return response.json()["access_token"]
