"""Verification tests list and detail."""

from __future__ import annotations

from playwright.sync_api import Page

from support.assertions import assert_locator_visible, assert_url_matches_regex


def open_tests_list(page: Page) -> None:
    page.goto("/tests")


def open_first_test_from_list(page: Page) -> None:
    open_tests_list(page)
    assert_locator_visible(
        page.get_by_role("heading", name="Verification tests"),
        description="tests list title",
        timeout_ms=30_000,
    )
    table = page.get_by_role("table")
    table.wait_for(state="visible", timeout=30_000)
    first_key_link = table.locator("tbody a").first
    assert_locator_visible(first_key_link, description="first test key link in table", timeout_ms=30_000)
    first_key_link.click()


def assert_test_detail_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/tests/\d+")
    assert_locator_visible(
        page.get_by_role("link", name="Back to tests"),
        description="back link to tests list",
    )
