"""Plain ``assert`` helpers for functional E2E checks (with short timeouts where needed)."""

from __future__ import annotations

import re
from typing import Pattern

from playwright.sync_api import Locator, Page


def assert_url_matches_regex(page: Page, pattern: str | Pattern[str], *, message: str | None = None) -> None:
    rx = re.compile(pattern) if isinstance(pattern, str) else pattern
    assert rx.search(page.url), message or f"URL {page.url!r} should match {rx.pattern!r}"


def assert_page_url_starts_with(page: Page, prefix: str) -> None:
    assert page.url.startswith(prefix), f"URL {page.url!r} should start with {prefix!r}"


def assert_locator_visible(locator: Locator, *, description: str, timeout_ms: float = 15_000) -> None:
    locator.wait_for(state="visible", timeout=timeout_ms)
    assert locator.is_visible(), description
