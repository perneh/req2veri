"""Bulk load dimensions from environment (defaults match full scenario)."""

from collections.abc import Mapping


def requirement_count(environ: Mapping[str, str] | None = None) -> int:
    return int((environ or {}).get("REQ2VERI_LOAD_REQS", "500"))


def subs_per_requirement(environ: Mapping[str, str] | None = None) -> int:
    return int((environ or {}).get("REQ2VERI_LOAD_SUBS_PER_REQ", "10"))


def tests_per_sub(environ: Mapping[str, str] | None = None) -> int:
    return int((environ or {}).get("REQ2VERI_LOAD_TESTS_PER_SUB", "2"))


def trend_version_count(environ: Mapping[str, str] | None = None) -> int:
    """How many test-object versions to create in the version-run trend load test."""
    return int((environ or {}).get("REQ2VERI_LOAD_TREND_VERSIONS", "4"))


def trend_verification_test_count(environ: Mapping[str, str] | None = None) -> int:
    """How many verification tests receive one run per version in the trend load test."""
    return int((environ or {}).get("REQ2VERI_LOAD_TREND_TESTS", "3"))
