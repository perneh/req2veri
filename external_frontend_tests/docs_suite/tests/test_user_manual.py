"""Generate screenshot-backed Markdown user manual (run: pytest docs_suite/tests/)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from support.flows import auth as auth_flow
from support.flows import nav as nav_flow
from support.manual_builder import ManualBuilder
from support.target import assert_origin_is_http


def _out_dir() -> Path:
    raw = os.environ.get("REQ2VERI_MANUAL_OUTPUT", "").strip()
    if raw:
        return Path(raw).resolve()
    return Path(__file__).resolve().parent.parent / "output"


@pytest.mark.user_manual
def test_generate_user_manual(english_page: Page, frontend_target: str) -> None:
    assert_origin_is_http(frontend_target)
    page = english_page
    manual = ManualBuilder(_out_dir())
    try:
        # --- Sign in
        manual.start_chapter(
            "01-sign-in",
            "Sign in",
            intro=(
                "Access to requirements, tests, and reports is **authenticated**. "
                "Use a user that exists in the system (e.g. seeded `demo`).\n"
            ),
        )
        auth_flow.open_login(page)
        expect(page.get_by_role("button", name="Sign in")).to_be_visible(timeout=15_000)
        manual.step(
            page,
            title="Login form",
            why="Only signed-in users can use dashboard, requirements, and test reporting.",
            how="Open `/login`, enter **Username** and **Password**, then click **Sign in**.",
            image_basename="login-form",
        )
        auth_flow.submit_sign_in(page)
        page.wait_for_url("**/dashboard", timeout=30_000)
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible(timeout=15_000)
        manual.step(
            page,
            title="Dashboard after sign-in",
            why="Confirms a successful session and shows high-level project status at a glance.",
            how="After a valid login, the app routes you to **Dashboard** automatically.",
            image_basename="dashboard-landing",
        )

        # --- Dashboard
        manual.start_chapter(
            "02-dashboard",
            "Dashboard",
            intro="The **Dashboard** summarizes requirements, tests, and recent test-run outcomes.\n",
        )
        nav_flow.click_nav_dashboard(page)
        nav_flow.assert_dashboard_page(page)
        manual.step(
            page,
            title="Summary tiles",
            why="Quickly see counts of requirements, tests, and pass/fail/block trends without opening lists.",
            how="Use the top link **Dashboard** (or the app title to go home, then dashboard if needed).",
            image_basename="dashboard",
        )

        # --- Requirements
        manual.start_chapter(
            "03-requirements",
            "Requirements",
            intro="**Requirements** are the top-level need statements you trace to verification tests.\n",
        )
        nav_flow.click_nav_requirements(page)
        nav_flow.assert_requirements_list_page(page)
        manual.step(
            page,
            title="Requirement list",
            why="You search and open requirements to read detail, add sub-requirements, and see approval metadata.",
            how="**Add/edit** → **Requirements** (or the **Requirements** entry in the same menu) opens the list.",
            image_basename="requirements-list",
        )

        # --- Sub-requirements overview
        manual.start_chapter(
            "04-overview",
            "Requirements overview (tree)",
            intro="A **hierarchical** view of each requirement and its sub-requirements.\n",
        )
        with page.expect_response(
            lambda r: r.status == 200 and "requirements/hierarchy" in r.url,
            timeout=60_000,
        ):
            nav_flow.click_nav_overview(page)
        nav_flow.assert_overview_page(page)
        # Page shows "Loading…" until /requirements/hierarchy returns; do not capture that state.
        expect(page.get_by_text("Loading…", exact=True)).to_be_hidden(timeout=30_000)
        manual.step(
            page,
            title="All requirements and sub-requirements",
            why="Understand structure and status across the project without opening each requirement one by one.",
            how="**Add/edit** → **Sub-requirements** to open the overview (URL `/requirements/overview`).",
            image_basename="overview-tree",
        )

        # --- Relations
        manual.start_chapter(
            "05-relations",
            "Requirement relations",
            intro="**Traceability** from a chosen requirement to related sub-requirements and tests.\n",
        )
        nav_flow.click_nav_relations(page)
        nav_flow.assert_relations_page(page)
        manual.step(
            page,
            title="Traceability view",
            why="Verify that a requirement is covered by the right sub-requirements and test cases for audits.",
            how="Click **Relations** in the bar, pick a requirement in the first column, then read the other columns.",
            image_basename="relations",
        )

        # --- Tests
        manual.start_chapter(
            "06-tests",
            "Verification tests",
            intro="**Verification tests** are the test cases you run against system versions and record results for.\n",
        )
        nav_flow.click_nav_tests(page)
        nav_flow.assert_tests_list_page(page)
        manual.step(
            page,
            title="Test list",
            why="Create and maintain test definitions and see how they link to requirements or sub-requirements.",
            how="**Add/edit** → **Tests** to open the catalog (URL `/tests`).",
            image_basename="tests-list",
        )

        # --- System versions
        manual.start_chapter(
            "07-system-versions",
            "System versions",
            intro="**System versions** represent the product or configuration build you report test results against.\n",
        )
        nav_flow.click_nav_versions(page)
        nav_flow.assert_versions_page(page)
        manual.step(
            page,
            title="List of system versions",
            why="Choose which version a test run targets when reporting; compare coverage across versions.",
            how="**System** → **List all system versions** opens `/systems`.",
            image_basename="system-list",
        )

        # --- Test report (search)
        manual.start_chapter(
            "08-test-report",
            "Test report",
            intro="**Test report** is where you record and browse results for a system version and test case.\n",
        )
        nav_flow.click_nav_test_report_search(page)
        nav_flow.assert_test_report_search_page(page)
        manual.step(
            page,
            title="Search by system version and test",
            why="Link stored runs to a specific version and test, with notes and who reported the run.",
            how="**Test report** → **Search by system version** — select version and test, then report or read rows.",
            image_basename="test-report-search",
        )

        # --- Test report trends
        manual.start_chapter(
            "09-test-report-trends",
            "Test report trends",
            intro="**Trends** show how test outcomes evolve over calendar time for reporting / retrospectives.\n",
        )
        nav_flow.click_nav_test_report_trends(page)
        nav_flow.assert_test_report_trends_page(page)
        manual.step(
            page,
            title="Trends over time",
            why="See whether quality is improving and spot days with clusters of fails or blockers.",
            how="**Test report** → **Trends** to open the chart (URL `/test-report/trends`).",
            image_basename="test-report-trends",
        )
    finally:
        manual.write_index()
