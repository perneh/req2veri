import uuid

from support import http, predicates


def _standalone_test_body(key: str) -> dict:
    return {
        "key": key[:32],
        "title": "Standalone VT",
        "description": "",
        "precondition": "",
        "action": "",
        "method": "analysis",
        "requirement_id": None,
        "sub_requirement_id": None,
        "expected_result": "",
    }


# Expected success


def test_post_standalone_verification_test(http_client, functional_headers) -> None:
    k = f"X{uuid.uuid4().hex}"[:32]
    r = http.post_json(http_client, "/tests", _standalone_test_body(k), headers=functional_headers)
    assert predicates.is_status(r, 201)
    body = predicates.json_body(r)
    assert body["requirement_id"] is None
    assert body["sub_requirement_id"] is None


def test_post_requirement_linked_test(http_client, functional_headers) -> None:
    u = uuid.uuid4().hex[:8]
    req = {
        "key": f"TR{u}"[:32],
        "title": "For linked test",
        "description": "",
        "status": "draft",
        "priority": "low",
    }
    pr = http.post_json(http_client, "/requirements", req, headers=functional_headers)
    assert predicates.is_status(pr, 201)
    rid = predicates.json_body(pr)["id"]
    tk = f"L{uuid.uuid4().hex}"[:32]
    body = {
        "key": tk,
        "title": "Linked VT",
        "description": "",
        "precondition": "",
        "action": "",
        "method": "test",
        "requirement_id": rid,
        "sub_requirement_id": None,
        "expected_result": "",
    }
    r = http.post_json(http_client, f"/requirements/{rid}/tests", body, headers=functional_headers)
    assert predicates.is_status(r, 201)
    assert predicates.json_body(r)["requirement_id"] == rid


def test_patch_links_standalone_test_to_requirement_then_removes_link(http_client, functional_headers) -> None:
    u = uuid.uuid4().hex[:8]
    req = {
        "key": f"TLR{u}"[:32],
        "title": "Requirement for link/unlink",
        "description": "",
        "status": "draft",
        "priority": "low",
    }
    pr = http.post_json(http_client, "/requirements", req, headers=functional_headers)
    assert predicates.is_status(pr, 201)
    rid = predicates.json_body(pr)["id"]

    tk = f"S{uuid.uuid4().hex}"[:32]
    cr = http.post_json(http_client, "/tests", _standalone_test_body(tk), headers=functional_headers)
    assert predicates.is_status(cr, 201)
    tid = predicates.json_body(cr)["id"]

    linked = http.patch_json(
        http_client,
        f"/tests/{tid}",
        {"requirement_id": rid, "sub_requirement_id": None},
        headers=functional_headers,
    )
    assert predicates.is_status(linked, 200)
    linked_body = predicates.json_body(linked)
    assert linked_body["requirement_id"] == rid
    assert linked_body["sub_requirement_id"] is None

    g1 = http.get(http_client, f"/tests/{tid}", headers=functional_headers)
    assert predicates.is_status(g1, 200)
    assert predicates.json_body(g1)["requirement_id"] == rid

    unlinked = http.patch_json(
        http_client,
        f"/tests/{tid}",
        {"requirement_id": None, "sub_requirement_id": None},
        headers=functional_headers,
    )
    assert predicates.is_status(unlinked, 200)
    unlinked_body = predicates.json_body(unlinked)
    assert unlinked_body["requirement_id"] is None
    assert unlinked_body["sub_requirement_id"] is None


def test_patch_links_standalone_test_to_sub_requirement(http_client, functional_headers) -> None:
    u = uuid.uuid4().hex[:8]
    pr = http.post_json(
        http_client,
        "/requirements",
        {
            "key": f"TLS{u}"[:32],
            "title": "Parent for sub link",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
        headers=functional_headers,
    )
    assert predicates.is_status(pr, 201)
    rid = predicates.json_body(pr)["id"]
    sr = http.post_json(
        http_client,
        f"/requirements/{rid}/subrequirements",
        {
            "key": f"SUBTLS{u}"[:48],
            "title": "Sub for link",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
        headers=functional_headers,
    )
    assert predicates.is_status(sr, 201)
    sid = predicates.json_body(sr)["id"]

    tk = f"U{uuid.uuid4().hex}"[:32]
    cr = http.post_json(http_client, "/tests", _standalone_test_body(tk), headers=functional_headers)
    assert predicates.is_status(cr, 201)
    tid = predicates.json_body(cr)["id"]

    linked = http.patch_json(
        http_client,
        f"/tests/{tid}",
        {"requirement_id": None, "sub_requirement_id": sid},
        headers=functional_headers,
    )
    assert predicates.is_status(linked, 200)
    lb = predicates.json_body(linked)
    assert lb["requirement_id"] is None
    assert lb["sub_requirement_id"] == sid


# Expected failure


def test_post_test_returns_409_for_duplicate_key(http_client, functional_headers) -> None:
    key = f"D{uuid.uuid4().hex}"[:32]
    body = _standalone_test_body(key)
    first = http.post_json(http_client, "/tests", body, headers=functional_headers)
    assert predicates.is_status(first, 201)
    second = http.post_json(http_client, "/tests", body, headers=functional_headers)
    assert predicates.is_status(second, 409)


def test_post_test_returns_422_when_both_parents_set(http_client, functional_headers) -> None:
    bad_key = f"B{uuid.uuid4().hex}"[:32]
    invalid = {
        "key": bad_key,
        "title": "Invalid linkage",
        "description": "",
        "precondition": "",
        "action": "",
        "method": "test",
        "requirement_id": 1,
        "sub_requirement_id": 1,
        "expected_result": "",
    }
    r = http.post_json(http_client, "/tests", invalid, headers=functional_headers)
    assert predicates.is_status(r, 422)


def test_patch_test_returns_404_when_linking_to_missing_requirement(http_client, functional_headers) -> None:
    tk = f"M{uuid.uuid4().hex}"[:32]
    cr = http.post_json(http_client, "/tests", _standalone_test_body(tk), headers=functional_headers)
    assert predicates.is_status(cr, 201)
    tid = predicates.json_body(cr)["id"]

    bad = http.patch_json(
        http_client,
        f"/tests/{tid}",
        {"requirement_id": 999_999_999, "sub_requirement_id": None},
        headers=functional_headers,
    )
    assert predicates.is_status(bad, 404)
