"""App bar navigation — functional asserts on URL and headings."""

from __future__ import annotations

from playwright.sync_api import Page

from support.flows import nav as nav_flow
from support.target import assert_origin_is_http


def test_nav_opens_tests_list(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    assert logged_in_page.url.startswith(frontend_target), logged_in_page.url
    nav_flow.click_nav_tests(logged_in_page)
    nav_flow.assert_tests_list_page(logged_in_page)


def test_nav_opens_requirements_list(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_requirements(logged_in_page)
    nav_flow.assert_requirements_list_page(logged_in_page)
