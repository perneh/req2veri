"""App bar navigation (English UI; labels match ``frontend/src/i18n/locales/en.json`` ``nav`` / ``app``)."""

from __future__ import annotations

from playwright.sync_api import Page

from support.assertions import assert_locator_visible, assert_url_matches_regex


def click_brand_home(page: Page) -> None:
    page.get_by_role("link", name="req2veri", exact=True).click()


def open_add_edit_menu(page: Page) -> None:
    add_edit_btn = page.get_by_role("button", name="Add/edit", exact=True)
    if add_edit_btn.count() > 0:
        add_edit_btn.click()


def click_nav_dashboard(page: Page) -> None:
    page.get_by_role("link", name="Dashboard", exact=True).click()


def click_nav_requirements(page: Page) -> None:
    add_edit_item = page.get_by_role("menuitem", name="Requirements", exact=True)
    if page.get_by_role("button", name="Add/edit", exact=True).count() > 0:
        open_add_edit_menu(page)
        add_edit_item.click()
        return
    page.get_by_role("link", name="Requirements", exact=True).click()


def click_nav_overview(page: Page) -> None:
    if page.get_by_role("button", name="Add/edit", exact=True).count() > 0:
        open_add_edit_menu(page)
        page.get_by_role("menuitem", name="Sub-requirements", exact=True).click()
        return
    page.get_by_role("link", name="All req. & sub-req.", exact=True).click()


def click_nav_relations(page: Page) -> None:
    page.get_by_role("link", name="Relations", exact=True).click()


def click_nav_tests(page: Page) -> None:
    if page.get_by_role("button", name="Add/edit", exact=True).count() > 0:
        open_add_edit_menu(page)
        page.get_by_role("menuitem", name="Tests", exact=True).click()
        return
    page.get_by_role("link", name="Tests", exact=True).click()


def click_nav_versions(page: Page) -> None:
    page.get_by_role("button", name="System", exact=True).click()
    page.get_by_role("menuitem", name="List all system versions", exact=True).click()


def click_nav_system_add(page: Page) -> None:
    page.get_by_role("button", name="System", exact=True).click()
    page.get_by_role("menuitem", name="Add system", exact=True).click()


def click_nav_system_expand(page: Page) -> None:
    page.get_by_role("button", name="System", exact=True).click()
    page.get_by_role("menuitem", name="Expand system version", exact=True).click()


def click_nav_test_report_search(page: Page) -> None:
    page.get_by_role("button", name="Test report", exact=True).click()
    page.get_by_role("menuitem", name="Search by system version", exact=True).click()


def click_nav_test_report_trends(page: Page) -> None:
    page.get_by_role("button", name="Test report", exact=True).click()
    page.get_by_role("menuitem", name="Trends", exact=True).click()


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


def assert_relations_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/requirements/relations$")
    assert_locator_visible(
        page.get_by_role("heading", name="Requirement relations"),
        description="requirement relations heading",
    )


def assert_versions_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/systems$")
    assert_locator_visible(
        page.get_by_role("heading", name="All system versions"),
        description="all system versions heading",
    )


def assert_system_add_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/systems/new$")
    assert_locator_visible(
        page.get_by_role("heading", name="Add system version"),
        description="add system version heading",
    )


def assert_system_expand_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/systems/expand$")
    assert_locator_visible(
        page.get_by_role("heading", name="Expand system version"),
        description="expand system version heading",
    )


def assert_test_report_search_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/test-report$")
    assert_locator_visible(
        page.get_by_role("heading", name="Test report"),
        description="test report heading",
    )


def assert_test_report_trends_page(page: Page) -> None:
    assert_url_matches_regex(page, r".*/test-report/trends$")
    assert_locator_visible(
        page.get_by_role("heading", name="Test case trends"),
        description="test report trends heading",
    )
