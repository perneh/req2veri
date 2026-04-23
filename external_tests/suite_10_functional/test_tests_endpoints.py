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
