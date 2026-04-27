"""One functional test per authenticated app-bar route (English labels)."""

from __future__ import annotations

from playwright.sync_api import Page

from support.flows import nav as nav_flow
from support.target import assert_origin_is_http


def test_nav_bar_dashboard(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    assert logged_in_page.url.startswith(frontend_target), logged_in_page.url
    nav_flow.click_nav_dashboard(logged_in_page)
    nav_flow.assert_dashboard_page(logged_in_page)


def test_nav_bar_requirements(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_requirements(logged_in_page)
    nav_flow.assert_requirements_list_page(logged_in_page)


def test_nav_bar_overview(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_overview(logged_in_page)
    nav_flow.assert_overview_page(logged_in_page)


def test_nav_bar_tests(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_tests(logged_in_page)
    nav_flow.assert_tests_list_page(logged_in_page)


def test_nav_bar_versions(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_versions(logged_in_page)
    nav_flow.assert_versions_page(logged_in_page)


def test_nav_bar_brand_when_authed_goes_to_dashboard(logged_in_page: Page, frontend_target: str) -> None:
    """App title link goes to ``/``, which redirects to the dashboard when a token exists."""
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_tests(logged_in_page)
    nav_flow.assert_tests_list_page(logged_in_page)
    nav_flow.click_brand_home(logged_in_page)
    nav_flow.assert_dashboard_page(logged_in_page)
