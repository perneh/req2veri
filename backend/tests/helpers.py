"""Shared helpers for API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def register_user(client: TestClient, username: str, *, email: str | None = None) -> None:
    client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email or f"{username}@example.com",
            "password": "pw12345678",
        },
    )


def register_and_token(client: TestClient, username: str = "u1", *, email: str | None = None) -> str:
    register_user(client, username, email=email)
    r = client.post("/auth/token", data={"username": username, "password": "pw12345678"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def register_and_token_as(client: TestClient, username: str) -> str:
    return register_and_token(client, username, email=f"{username}@example.com")


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
