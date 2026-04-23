"""Browser locale helpers for stable English selectors."""

from __future__ import annotations

from playwright.sync_api import Page


def force_english_ui(page: Page) -> None:
    page.add_init_script("() => { localStorage.setItem('req2veri_lang', 'en'); }")
