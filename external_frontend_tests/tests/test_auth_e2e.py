"""Login and routing smoke tests."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect


def test_unauthenticated_root_redirects_to_login(english_page: Page) -> None:
    english_page.goto("/")
    expect(english_page).to_have_url(re.compile(r".*/login$"))


def test_sign_in_reaches_dashboard(logged_in_page: Page) -> None:
    expect(logged_in_page.get_by_role("heading", name="Dashboard")).to_be_visible()
