"""Playwright browser fixtures via pytest-playwright; shared UI helpers."""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import Page

from support import env as fe_env


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--host",
        action="store",
        default=None,
        metavar="HOST",
        help="Frontend host when REQ2VERI_FRONTEND_BASE_URL is unset (overrides REQ2VERI_FRONTEND_HOST). Default: 127.0.0.1",
    )
    parser.addoption(
        "--port",
        action="store",
        default=None,
        metavar="PORT",
        help="Frontend port when REQ2VERI_FRONTEND_BASE_URL is unset (overrides REQ2VERI_FRONTEND_PORT). Default: 5173",
    )
    parser.addoption(
        "--allow-offline",
        action="store_true",
        default=False,
        help="Do not probe the frontend URL before tests (you get Playwright errors if nothing is listening).",
    )


def _resolved_frontend_origin(config: pytest.Config) -> str:
    return fe_env.resolve_frontend_root(
        os.environ,
        cli_host=config.getoption("host"),
        cli_port=config.getoption("port"),
    )


def pytest_configure(config: pytest.Config) -> None:
    """Keep PYTEST_BASE_URL aligned for tooling; Playwright itself uses ``browser_context_args`` below."""
    os.environ["PYTEST_BASE_URL"] = _resolved_frontend_origin(config)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Fail fast with a clear message instead of many Playwright ``ERR_CONNECTION_REFUSED`` errors."""
    import urllib.error
    import urllib.parse
    import urllib.request

    cfg = session.config
    if cfg.getoption("allow_offline") or os.environ.get("REQ2VERI_E2E_ALLOW_OFFLINE", "").strip() in (
        "1",
        "true",
        "yes",
    ):
        return

    origin = _resolved_frontend_origin(cfg)
    try:
        req = urllib.request.Request(f"{origin}/", method="GET", headers={"Accept": "*/*"})
        urllib.request.urlopen(req, timeout=5)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        port = urllib.parse.urlparse(origin).port
        hint_4173 = (
            "\n  Hint: `npm run dev` uses port 5173 by default. If the UI is on 5173, run pytest without "
            "`--port 4173`, or use `pytest --port 5173`.\n"
            if port == 4173
            else ""
        )
        pytest.exit(
            f"\n[external_frontend_tests] No HTTP server at {origin} ({e!r}).{hint_4173}\n"
            "  Start the SPA on that origin, then rerun pytest. Typical pairs:\n"
            "    cd ../frontend && npm run dev          &&  pytest --port 5173   # or plain pytest\n"
            "    cd ../frontend && npm run preview -- --host 127.0.0.1 --port 4173  &&  pytest --port 4173\n"
            "  To skip this check: pytest --allow-offline  (or REQ2VERI_E2E_ALLOW_OFFLINE=1)\n",
            returncode=1,
        )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, request: pytest.FixtureRequest) -> dict:
    """pytest-base-url / env timing can leave relative ``page.goto`` paths without an origin; set explicitly."""
    origin = _resolved_frontend_origin(request.config)
    return {**browser_context_args, "base_url": origin}


def _e2e_credentials() -> tuple[str, str]:
    """Defaults match seeded `demo` user from `backend/scripts/seed.py`."""
    u = os.environ.get("REQ2VERI_E2E_USERNAME", "demo")
    p = os.environ.get("REQ2VERI_E2E_PASSWORD", "demo12345")
    return u, p


def _force_english_locale(page: Page) -> None:
    page.add_init_script("() => { localStorage.setItem('req2veri_lang', 'en'); }")


def _log_in(page: Page) -> None:
    _force_english_locale(page)
    page.goto("/login")
    user, password = _e2e_credentials()
    page.get_by_label("Username").fill(user)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("**/dashboard", timeout=30_000)


@pytest.fixture
def english_page(page: Page) -> Page:
    """Stable English labels for role/name selectors."""
    _force_english_locale(page)
    yield page


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    _log_in(page)
    yield page
