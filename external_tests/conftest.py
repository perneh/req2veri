import os
from collections.abc import Iterator

import httpx
import pytest

from support import env, http as http_support

_SUITE_ORDER = ("suite_00_empty", "suite_10_functional", "suite_99_load")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Run suites in order: empty-system checks → functional groups → bulk load."""

    def suite_rank(item: pytest.Item) -> tuple[int, str]:
        path = str(item.fspath)
        for i, prefix in enumerate(_SUITE_ORDER):
            if prefix in path:
                return (i, item.nodeid)
        return (len(_SUITE_ORDER), item.nodeid)

    items.sort(key=suite_rank)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Target API — set REQ2VERI_BASE_URL or REQ2VERI_API_HOST / REQ2VERI_API_PORT in the environment."""
    return env.resolve_api_root(environ=os.environ)


@pytest.fixture(scope="session")
def http_client(base_url: str) -> Iterator[httpx.Client]:
    """Session-scoped so session-scoped auth in functional suite can reuse the same client."""
    with http_support.client(base_url) as client:
        yield client
