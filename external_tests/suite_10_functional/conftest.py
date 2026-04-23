"""Shared auth for functional endpoint groups (one session user, unique keys per test)."""

import pytest

from support import auth, flow


@pytest.fixture(scope="session")
def functional_token(http_client) -> str:
    return flow.register_and_token(http_client)


@pytest.fixture
def functional_headers(functional_token: str) -> dict[str, str]:
    return auth.bearer_headers(functional_token)
