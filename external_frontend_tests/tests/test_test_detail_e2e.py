"""Verification test detail page (requires ≥1 test in the API)."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect


def test_first_listed_test_opens_detail_with_back_link(logged_in_page: Page) -> None:
    logged_in_page.goto("/tests")
    expect(logged_in_page.get_by_role("heading", name="Verification tests")).to_be_visible()
    table = logged_in_page.get_by_role("table")
    table.wait_for(state="visible", timeout=30_000)
    first_key_link = table.locator("tbody a").first
    expect(first_key_link).to_be_visible(timeout=30_000)
    first_key_link.click()
    expect(logged_in_page).to_have_url(re.compile(r".*/tests/\d+"))
    expect(logged_in_page.get_by_role("link", name="Back to tests")).to_be_visible()
