"""App bar navigation."""

from __future__ import annotations

from playwright.sync_api import Page

from support.assertions import assert_locator_visible, assert_url_matches_regex


def click_nav_tests(page: Page) -> None:
    page.get_by_role("link", name="Tests", exact=True).click()


def click_nav_requirements(page: Page) -> None:
    page.get_by_role("link", name="Requirements", exact=True).click()


def assert_tests_list_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/tests$")
    assert_locator_visible(
        page.get_by_role("heading", name="Verification tests"),
        description="verification tests list heading",
    )


def assert_requirements_list_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/requirements$")
    assert_locator_visible(
        page.get_by_role("heading", name="Requirements"),
        description="requirements list heading",
    )
