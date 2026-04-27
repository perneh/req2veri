"""App bar navigation (English UI; labels match ``frontend/src/i18n/locales/en.json`` ``nav`` / ``app``)."""

from __future__ import annotations

from playwright.sync_api import Page

from support.assertions import assert_locator_visible, assert_url_matches_regex


def click_brand_home(page: Page) -> None:
    page.get_by_role("link", name="req2veri", exact=True).click()


def click_nav_dashboard(page: Page) -> None:
    page.get_by_role("link", name="Dashboard", exact=True).click()


def click_nav_requirements(page: Page) -> None:
    page.get_by_role("link", name="Requirements", exact=True).click()


def click_nav_overview(page: Page) -> None:
    page.get_by_role("link", name="All req. & sub-req.", exact=True).click()


def click_nav_tests(page: Page) -> None:
    page.get_by_role("link", name="Tests", exact=True).click()


def click_nav_versions(page: Page) -> None:
    page.get_by_role("link", name="Test versions", exact=True).click()


def assert_dashboard_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/dashboard$")
    assert_locator_visible(
        page.get_by_role("heading", name="Dashboard"),
        description="dashboard heading",
    )


def assert_requirements_list_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/requirements$")
    assert_locator_visible(
        page.get_by_role("heading", name="Requirements"),
        description="requirements list heading",
    )


def assert_overview_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/requirements/overview$")
    assert_locator_visible(
        page.get_by_role("heading", name="All requirements and sub-requirements"),
        description="requirements overview heading",
    )


def assert_tests_list_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/tests$")
    assert_locator_visible(
        page.get_by_role("heading", name="Verification tests"),
        description="verification tests list heading",
    )


def assert_versions_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/versions$")
    assert_locator_visible(
        page.get_by_role("heading", name="Test object versions"),
        description="test object versions heading",
    )
