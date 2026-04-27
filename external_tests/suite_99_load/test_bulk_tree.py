"""Create many requirements, sub-requirements, and tests (default: 500 × 10 × 2)."""

import os
import uuid
from itertools import count

import pytest

from support import auth, dashboard, flow, http, load_scale, predicates


@pytest.mark.load
def test_bulk_requirements_subs_and_tests(http_client) -> None:
    n_req = load_scale.requirement_count(os.environ)
    n_sub = load_scale.subs_per_requirement(os.environ)
    n_tst = load_scale.tests_per_sub(os.environ)

    token = flow.register_and_token(http_client)
    headers = auth.bearer_headers(token)
    test_creator_headers = [auth.bearer_headers(flow.register_and_token(http_client)) for _ in range(10)]
    run = uuid.uuid4().hex[:8]
    key_seq = count(0)
    actor_seq = count(0)

    def next_test_body() -> dict:
        n = next(key_seq)
        key = f"T{run}{n:05d}"[:32]
        return {
            "key": key,
            "title": f"Load VT {run}-{n}",
            "description": "",
            "precondition": "",
            "action": "",
            "method": "test",
            "requirement_id": None,
            "sub_requirement_id": None,
            "expected_result": "",
        }

    before = dashboard.fetch_summary(http_client, headers)
    assert predicates.is_status(before, 200)
    b0 = predicates.json_body(before)

    for i in range(n_req):
        rk = f"R{run}{i:03d}"[:32]
        rr = http.post_json(
            http_client,
            "/requirements",
            {
                "key": rk,
                "title": f"Load {i}",
                "description": "",
                "status": "draft",
                "priority": "low",
            },
            headers=headers,
        )
        assert predicates.is_status(rr, 201), rr.text
        rid = predicates.json_body(rr)["id"]

        for j in range(n_sub):
            sk = f"S{run}{i:03d}{j:02d}"[:48]
            sr = http.post_json(
                http_client,
                f"/requirements/{rid}/subrequirements",
                {
                    "key": sk,
                    "title": f"Sub {j}",
                    "description": "",
                    "status": "draft",
                    "priority": "low",
                },
                headers=headers,
            )
            assert predicates.is_status(sr, 201), sr.text
            sid = predicates.json_body(sr)["id"]

            for _ in range(n_tst):
                h_test = test_creator_headers[next(actor_seq) % 10]
                tr = http.post_json(
                    http_client,
                    f"/subrequirements/{sid}/tests",
                    next_test_body(),
                    headers=h_test,
                )
                assert predicates.is_status(tr, 201), tr.text

    after = dashboard.fetch_summary(http_client, headers)
    assert predicates.is_status(after, 200)
    a0 = predicates.json_body(after)

    assert a0["requirements_total"] == b0["requirements_total"] + n_req
    assert a0["subrequirements_total"] == b0["subrequirements_total"] + n_req * n_sub
    assert a0["tests_total"] == b0["tests_total"] + n_req * n_sub * n_tst
