"""E2E login secrets from the environment (defaults: seeded ``demo`` user)."""

from __future__ import annotations

import os


def e2e_username() -> str:
    return os.environ.get("REQ2VERI_E2E_USERNAME", "demo")


def e2e_password() -> str:
    return os.environ.get("REQ2VERI_E2E_PASSWORD", "demo12345")
