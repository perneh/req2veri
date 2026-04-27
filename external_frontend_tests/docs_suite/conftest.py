"""Local pytest hooks for the documentation / screenshot suite."""

from __future__ import annotations


def pytest_configure(config):  # type: ignore[no-untyped-def]
    config.addinivalue_line(
        "markers",
        "user_manual: generates screenshot-backed markdown (slow; optional in CI)",
    )
