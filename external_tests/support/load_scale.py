"""Bulk load dimensions from environment (defaults match full scenario)."""

from collections.abc import Mapping


def requirement_count(environ: Mapping[str, str] | None = None) -> int:
    return int((environ or {}).get("REQ2VERI_LOAD_REQS", "500"))


def subs_per_requirement(environ: Mapping[str, str] | None = None) -> int:
    return int((environ or {}).get("REQ2VERI_LOAD_SUBS_PER_REQ", "10"))


def tests_per_sub(environ: Mapping[str, str] | None = None) -> int:
    return int((environ or {}).get("REQ2VERI_LOAD_TESTS_PER_SUB", "2"))
