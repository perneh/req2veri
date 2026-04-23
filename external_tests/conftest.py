import os
from collections.abc import Iterator

import httpx
import pytest

from support import env, http as http_support

_SUITE_ORDER = ("suite_00_empty", "suite_10_functional", "suite_99_load")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--req2veri-base-url",
        action="store",
        default=None,
        help="Full API base URL (overrides --host/--port and REQ2VERI_BASE_URL)",
    )
    parser.addoption(
        "--host",
        action="store",
        default=None,
        help="API hostname or IP (default 127.0.0.1 if no REQ2VERI_BASE_URL)",
    )
    parser.addoption(
        "--port",
        action="store",
        default=None,
        help="API port (default 8000 if no REQ2VERI_BASE_URL)",
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
def base_url(pytestconfig: pytest.Config) -> str:
    return env.resolve_api_root(
        cli_base_url=pytestconfig.getoption("--req2veri-base-url", default=None),
        environ=os.environ,
        host=pytestconfig.getoption("--host", default=None),
        port=pytestconfig.getoption("--port", default=None),
    )


@pytest.fixture(scope="session")
def http_client(base_url: str) -> Iterator[httpx.Client]:
    """Session-scoped so session-scoped auth in functional suite can reuse the same client."""
    with http_support.client(base_url) as client:
        yield client
