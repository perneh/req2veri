"""Sign-in and unauthenticated entry flows."""

from __future__ import annotations

from playwright.sync_api import Page

from support.assertions import assert_url_matches_regex
from support.credentials import e2e_password, e2e_username
from support.locale import force_english_ui


def open_app_root(page: Page, *, wait_for_login_redirect: bool = False) -> None:
    """Open ``/``. For guests, React routes to ``/login`` asynchronously — set ``wait_for_login_redirect``."""
    force_english_ui(page)
    page.goto("/")
    if wait_for_login_redirect:
        page.wait_for_url("**/login", timeout=15_000)


def open_login(page: Page) -> None:
    force_english_ui(page)
    page.goto("/login")


def submit_sign_in(page: Page) -> None:
    page.get_by_label("Username").fill(e2e_username())
    page.get_by_label("Password").fill(e2e_password())
    page.get_by_role("button", name="Sign in").click()


def sign_in_as_configured_demo_user(page: Page) -> None:
    open_login(page)
    submit_sign_in(page)
    page.wait_for_url("**/dashboard", timeout=30_000)
    assert_url_matches_regex(page, r".*/dashboard")


def assert_login_shell_visible(page: Page) -> None:
    assert page.get_by_role("button", name="Sign in").is_visible(), "sign-in button should be visible on login"
