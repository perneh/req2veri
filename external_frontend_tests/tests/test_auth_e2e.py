"""Login and routing — asserts + flows; ``frontend_target`` reflects ``--host`` / ``--port``."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from support.assertions import assert_locator_visible, assert_url_matches_regex
from support.flows import auth as auth_flow
from support.target import assert_origin_is_http, assert_origin_host, assert_origin_port


def test_playwright_base_url_matches_resolved_target(page: Page, frontend_target: str) -> None:
    """Functional check that CLI/env resolution is the same origin the browser uses."""
    assert_origin_is_http(frontend_target)
    auth_flow.open_login(page)
    assert page.url.startswith(frontend_target), f"expected {page.url!r} to start with {frontend_target!r}"
    assert page.url.rstrip("/").endswith("/login"), f"expected login path in {page.url!r}"


def test_unauthenticated_root_redirects_to_login(english_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    auth_flow.open_app_root(english_page, wait_for_login_redirect=True)
    assert_url_matches_regex(english_page, r".*/login$")
    auth_flow.assert_login_shell_visible(english_page)


def test_sign_in_reaches_dashboard(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    assert logged_in_page.url.startswith(frontend_target), logged_in_page.url
    assert_locator_visible(
        logged_in_page.get_by_role("heading", name="Dashboard"),
        description="dashboard heading after sign-in",
    )


def test_host_port_cli_override_reflected_in_target(request: pytest.FixtureRequest, frontend_target: str) -> None:
    """When ``--host`` / ``--port`` are passed, the session target must match (defaults otherwise)."""
    cfg = request.config
    host_opt = cfg.getoption("host")
    port_opt = cfg.getoption("port")
    if host_opt is not None:
        assert_origin_host(frontend_target, str(host_opt))
    if port_opt is not None:
        assert_origin_port(frontend_target, int(str(port_opt)))
