import os
from collections.abc import Iterator

import httpx
import pytest

from support import env, http as http_support

_SUITE_ORDER = ("suite_00_empty", "suite_10_functional", "suite_99_load")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--host",
        action="store",
        default=None,
        metavar="HOST",
        help="API host when REQ2VERI_BASE_URL is unset (overrides REQ2VERI_API_HOST). Default: 127.0.0.1",
    )
    parser.addoption(
        "--port",
        action="store",
        default=None,
        metavar="PORT",
        help="API port when REQ2VERI_BASE_URL is unset (overrides REQ2VERI_API_PORT). Default: 8000",
    )


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
def base_url(request: pytest.FixtureRequest) -> str:
    """Target API — REQ2VERI_BASE_URL, or host/port from env and optional ``--host`` / ``--port``."""
    return env.resolve_api_root(
        environ=os.environ,
        cli_host=request.config.getoption("host"),
        cli_port=request.config.getoption("port"),
    )


@pytest.fixture(scope="session")
def http_client(base_url: str) -> Iterator[httpx.Client]:
    """Session-scoped so session-scoped auth in functional suite can reuse the same client."""
    with http_support.client(base_url) as client:
        yield client
