"""Requirement relations page flows."""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from support.assertions import assert_locator_visible, assert_url_matches_regex


def open_relations_page(page: Page) -> None:
    page.goto("/requirements/relations")


def assert_relations_layout(page: Page) -> None:
    assert_url_matches_regex(page, r".*/requirements/relations$")
    assert_locator_visible(
        page.get_by_role("heading", name="Requirement relations"),
        description="relations page title",
    )
    assert_locator_visible(
        page.get_by_text("Requirement", exact=True).first,
        description="column 1 heading",
    )
    assert_locator_visible(
        page.get_by_text("Related requirements", exact=True).first,
        description="column 2 heading",
    )
    assert_locator_visible(
        page.get_by_text("Related tests", exact=True).first,
        description="column 3 heading",
    )


def requirements_rows(page: Page) -> Locator:
    return page.locator("table").first.locator("tbody tr")


def select_first_requirement(page: Page) -> None:
    row = requirements_rows(page).first
    row.wait_for(state="visible", timeout=30_000)
    row.click()
    # Traceability query fills the two right-hand tables; count() does not auto-wait.
    expect(page.locator("table")).to_have_count(3, timeout=30_000)


def assert_related_columns_render(page: Page) -> None:
    # Two right-side tables mount after traceability loads; locator.count() does not wait.
    tables = page.locator("table")
    expect(tables).to_have_count(3, timeout=30_000)
    assert_locator_visible(tables.nth(1), description="related requirements table")
    assert_locator_visible(tables.nth(2), description="related tests table")
