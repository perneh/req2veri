"""System expand page E2E tests."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from support.flows import nav as nav_flow
from support.target import assert_origin_is_http


def test_system_expand_test_title_opens_test_detail(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_system_expand(logged_in_page)
    nav_flow.assert_system_expand_page(logged_in_page)

    # Expand first system accordion and click first linked test title if present.
    expand_buttons = logged_in_page.locator("button[aria-expanded]")
    if expand_buttons.count() == 0:
        pytest.skip("No system versions to expand")
    expand_buttons.first.click()

    test_links = logged_in_page.locator('a[href^="/tests/"]')
    if test_links.count() == 0:
        pytest.skip("No reported test links in expanded system version")
    test_links.first.click()
    assert "/tests/" in logged_in_page.url
