"""Composed API flows returning values or raising on failure."""

from __future__ import annotations

import httpx

from support import auth, predicates


def register_and_token(
    client: httpx.Client,
    *,
    password: str = "ExtPw12345678!",
) -> str:
    username = auth.unique_username()
    reg = auth.register(client, auth.register_payload(username=username, password=password))
    if not predicates.is_status(reg, 201):
        raise RuntimeError(f"register failed: {reg.status_code} {reg.text}")
    tok = auth.token(client, username=username, password=password)
    if not predicates.is_status(tok, 200):
        raise RuntimeError(f"token failed: {tok.status_code} {tok.text}")
    return auth.access_token(tok)
