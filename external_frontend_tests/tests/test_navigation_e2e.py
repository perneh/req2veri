"""App bar navigation."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect


def test_nav_opens_tests_list(logged_in_page: Page) -> None:
    logged_in_page.get_by_role("link", name="Tests", exact=True).click()
    expect(logged_in_page).to_have_url(re.compile(r".*/tests$"))
    expect(logged_in_page.get_by_role("heading", name="Verification tests")).to_be_visible()


def test_nav_opens_requirements_list(logged_in_page: Page) -> None:
    logged_in_page.get_by_role("link", name="Requirements", exact=True).click()
    expect(logged_in_page).to_have_url(re.compile(r".*/requirements$"))
    expect(logged_in_page.get_by_role("heading", name="Requirements")).to_be_visible()
