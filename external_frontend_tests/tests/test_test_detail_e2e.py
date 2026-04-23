"""Verification test detail — list → first row → detail asserts."""

from __future__ import annotations

from playwright.sync_api import Page

from support.flows import verification_tests as vt_flow
from support.target import assert_origin_is_http


def test_first_listed_test_opens_detail_with_back_link(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    assert logged_in_page.url.startswith(frontend_target), logged_in_page.url
    vt_flow.open_first_test_from_list(logged_in_page)
    vt_flow.assert_test_detail_page(logged_in_page)
