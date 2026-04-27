"""Load-suite: test report endpoint over 10 system versions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import pytest

from support import auth, flow, http, predicates


@pytest.mark.load
def test_load_test_report_for_10_versions(http_client) -> None:
    """Report one test-case result across 10 versions and verify persistence."""
    token = flow.register_and_token(http_client)
    headers = auth.bearer_headers(token)
    run = uuid.uuid4().hex[:8]

    req = http.post_json(
        http_client,
        "/requirements",
        {
            "key": f"RPT{run}"[:32],
            "title": "Report anchor requirement",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
        headers=headers,
    )
    assert predicates.is_status(req, 201), req.text
    rid = int(predicates.json_body(req)["id"])

    sub = http.post_json(
        http_client,
        f"/requirements/{rid}/subrequirements",
        {
            "key": f"RPTSUB{run}"[:48],
            "title": f"Report anchor sub {run}",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
        headers=headers,
    )
    assert predicates.is_status(sub, 201), sub.text
    sid = int(predicates.json_body(sub)["id"])

    test_case = http.post_json(
        http_client,
        f"/subrequirements/{sid}/tests",
        {
            "key": f"RPTT{run}"[:32],
            "title": f"Report anchor test case {run}",
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
    assert predicates.is_status(test_case, 201), test_case.text
    tid = int(predicates.json_body(test_case)["id"])

    version_ids: list[int] = []
    for i in range(10):
        vr = http.post_json(
            http_client,
            "/test-object-versions",
            {
                "key": f"RPTV{run}{i:02d}{uuid.uuid4().hex[:18]}"[:64],
                "name": f"System version {i + 1}",
                "description": f"report slot {i}",
            },
            headers=headers,
        )
        assert predicates.is_status(vr, 201), vr.text
        version_ids.append(int(predicates.json_body(vr)["id"]))

    statuses = ("not_run", "passed", "failed", "blocked")
    for i, vid in enumerate(version_ids):
        put = http.put_json(
            http_client,
            f"/test-object-versions/{vid}/runs/{tid}",
            {
                "status": statuses[i % len(statuses)],
                "information": f"report info for version {i + 1}",
                "ran_at": (datetime(2026, 2, 1, tzinfo=timezone.utc) + timedelta(days=i)).isoformat(),
            },
            headers=headers,
        )
        assert predicates.is_status(put, 200), put.text
        body = predicates.json_body(put)
        assert body["verification_test_id"] == tid
        assert body["test_object_version_id"] == vid
        assert body["information"] == f"report info for version {i + 1}"

    for i, vid in enumerate(version_ids):
        listed = http.get(http_client, f"/test-object-versions/{vid}/runs", headers=headers)
        assert predicates.is_status(listed, 200), listed.text
        rows = predicates.json_body(listed)
        assert len(rows) >= 1
        match = next((r for r in rows if int(r["verification_test_id"]) == tid), None)
        assert match is not None
        assert match["information"] == f"report info for version {i + 1}"
