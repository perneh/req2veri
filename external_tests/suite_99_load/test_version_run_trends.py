"""Load-suite: record TestRuns against several TestObjectVersions for trend-style checks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import uuid

import pytest

from support import auth, flow, http, load_scale, predicates


def _status_matrix(n_versions: int, n_tests: int) -> list[list[str]]:
    """Deterministic status per (version_index, test_index) using a short cycle."""
    cycle = ("not_run", "passed", "failed", "blocked")
    return [[cycle[(vi + ti) % len(cycle)] for ti in range(n_tests)] for vi in range(n_versions)]


@pytest.mark.load
def test_load_records_runs_across_versions_for_per_test_and_per_version_trends(http_client) -> None:
    """
    Creates multiple test-object versions and several verification tests, then posts one run
    per (version, test) with varied statuses. Asserts GET .../runs per version matches the matrix
    and that a single verification test sees different outcomes across versions (trend signal).
    """
    n_versions = load_scale.trend_version_count(os.environ)
    n_tests = load_scale.trend_verification_test_count(os.environ)
    assert n_versions >= 2
    assert n_tests >= 100

    token = flow.register_and_token(http_client)
    headers = auth.bearer_headers(token)
    run = uuid.uuid4().hex[:8]

    version_ids: list[int] = []
    for i in range(n_versions):
        key = f"TV{run}{i:02d}{uuid.uuid4().hex[:20]}"[:64]
        vr = http.post_json(
            http_client,
            "/test-object-versions",
            {"key": key, "name": f"Load trend v{i}", "description": f"slot {i}"},
            headers=headers,
        )
        assert predicates.is_status(vr, 201), vr.text
        version_ids.append(int(predicates.json_body(vr)["id"]))

    rk = f"RTR{run}"[:32]
    rr = http.post_json(
        http_client,
        "/requirements",
        {
            "key": rk,
            "title": f"Trend anchor {run}",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
        headers=headers,
    )
    assert predicates.is_status(rr, 201), rr.text
    rid = int(predicates.json_body(rr)["id"])

    sk = f"STR{run}"[:48]
    sr = http.post_json(
        http_client,
        f"/requirements/{rid}/subrequirements",
        {
            "key": sk,
            "title": f"Trend sub {run}",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
        headers=headers,
    )
    assert predicates.is_status(sr, 201), sr.text
    sid = int(predicates.json_body(sr)["id"])

    test_ids: list[int] = []
    for ti in range(n_tests):
        key = f"TT{run}{ti:02d}{uuid.uuid4().hex[:18]}"[:32]
        tr = http.post_json(
            http_client,
            f"/subrequirements/{sid}/tests",
            {
                "key": key,
                    "title": f"Trend VT {run}-{ti}",
                "description": "",
                "precondition": "",
                "action": "",
                "method": "test",
                "requirement_id": None,
                "sub_requirement_id": sid,
                "expected_result": "",
            },
            headers=headers,
        )
        assert predicates.is_status(tr, 201), tr.text
        test_ids.append(int(predicates.json_body(tr)["id"]))

    matrix = _status_matrix(n_versions, n_tests)
    for vi, vid in enumerate(version_ids):
        for ti, tid in enumerate(test_ids):
            st = matrix[vi][ti]
            pr = http.post_json(
                http_client,
                f"/test-object-versions/{vid}/runs",
                {
                    "verification_test_id": tid,
                    "status": st,
                    "information": f"info v{vi} t{ti}",
                    "ran_at": (
                        datetime(2026, 1, 1, tzinfo=timezone.utc)
                        + timedelta(days=vi, minutes=ti)
                    ).isoformat(),
                },
                headers=headers,
            )
            assert predicates.is_status(pr, 201), pr.text
            body = predicates.json_body(pr)
            assert body["verification_test_id"] == tid
            assert body["test_object_version_id"] == vid
            assert body["status"] == st

    for vi, vid in enumerate(version_ids):
        lr = http.get(http_client, f"/test-object-versions/{vid}/runs", headers=headers)
        assert predicates.is_status(lr, 200), lr.text
        runs = predicates.json_body(lr)
        assert len(runs) == n_tests
        by_tid = {int(r["verification_test_id"]): r for r in runs}
        for ti, tid in enumerate(test_ids):
            row = by_tid[tid]
            assert row["status"] == matrix[vi][ti]
            assert row["test_object_version_id"] == vid
            assert f"v{vi}" in row.get("information", "")

    # Per verification test: outcomes differ across versions (trend / history signal)
    for ti, tid in enumerate(test_ids):
        across = [matrix[vi][ti] for vi in range(n_versions)]
        assert len(set(across)) >= 2, f"test slot {ti} should vary across versions, got {across}"

    # Per version: not all tests share the same status when n_tests >= 2
    for vi in range(n_versions):
        row_statuses = [matrix[vi][ti] for ti in range(n_tests)]
        assert len(set(row_statuses)) >= 2, f"version slot {vi} should mix statuses, got {row_statuses}"
