"""Tests that *must* fail so Playwright writes screenshots under ``test-results/`` (``--screenshot only-on-failure``).

Run explicitly (do not merge into CI as green): ``pytest screen_fail_suites/``
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from support.assertions import assert_url_matches_regex
from support.flows import auth as auth_flow
from support.target import assert_origin_is_http

pytestmark = pytest.mark.screen_fail


def test_fails_on_impossible_substring_in_login_page(page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    auth_flow.open_login(page)
    assert "___PLAYWRIGHT_INTENTIONAL_FAILURE___" in page.content()


def test_fails_on_wrong_url_assertion(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    assert_url_matches_regex(logged_in_page, r".*/this-route-does-not-exist$")
