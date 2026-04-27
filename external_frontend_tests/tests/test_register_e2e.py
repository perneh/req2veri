"""Register a new user through the UI and end up on the dashboard."""

from __future__ import annotations

import uuid

from playwright.sync_api import Page

from support.assertions import assert_locator_visible
from support.flows import auth as auth_flow
from support.target import assert_origin_is_http


def test_register_new_user_and_sign_in_via_ui(page: Page, frontend_target: str) -> None:
    suffix = uuid.uuid4().hex[:12]
    username = f"e2e_{suffix}"
    email = f"{username}@example.com"
    password = "pw12345678"

    assert_origin_is_http(frontend_target)
    auth_flow.register_new_user_and_land_on_dashboard(
        page,
        username=username,
        email=email,
        password=password,
    )
    assert page.url.startswith(frontend_target), page.url
    assert_locator_visible(
        page.get_by_role("heading", name="Dashboard"),
        description="dashboard after register + auto login",
    )
