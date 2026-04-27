"""Relations page E2E tests."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from support.flows import nav as nav_flow
from support.flows import relations as relations_flow
from support.target import assert_origin_is_http


def test_relations_page_renders_three_columns(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    assert logged_in_page.url.startswith(frontend_target), logged_in_page.url
    relations_flow.open_relations_page(logged_in_page)
    relations_flow.assert_relations_layout(logged_in_page)


def test_relations_select_requirement_shows_related_requirements_and_tests(
    logged_in_page: Page, frontend_target: str
) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_relations(logged_in_page)
    relations_flow.assert_relations_layout(logged_in_page)
    relations_flow.select_first_requirement(logged_in_page)
    relations_flow.assert_related_columns_render(logged_in_page)


def test_relations_related_test_title_opens_test_detail(logged_in_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    nav_flow.click_nav_relations(logged_in_page)
    relations_flow.select_first_requirement(logged_in_page)
    test_links = logged_in_page.locator("table").nth(2).locator("tbody tr td:nth-child(2) a")
    if test_links.count() == 0:
        pytest.skip("No related test link available for selected requirement")
    test_links.first.click()
    assert "/tests/" in logged_in_page.url
