import uuid

from support import http, predicates


def _req_body() -> dict:
    u = uuid.uuid4().hex[:8]
    return {
        "key": f"SR{u}"[:32],
        "title": "Parent for sub",
        "description": "",
        "status": "draft",
        "priority": "low",
    }


def _sub_body(suffix: str) -> dict:
    return {
        "key": f"SUB{suffix}"[:48],
        "title": "Sub",
        "description": "",
        "status": "draft",
        "priority": "medium",
    }


def _create_parent_requirement(http_client, functional_headers) -> int:
    pr = http.post_json(http_client, "/requirements", _req_body(), headers=functional_headers)
    assert predicates.is_status(pr, 201)
    return predicates.json_body(pr)["id"]


# Expected success


def test_subrequirements_create_list_get(http_client, functional_headers) -> None:
    rid = _create_parent_requirement(http_client, functional_headers)

    u = uuid.uuid4().hex[:6]
    sr = http.post_json(
        http_client,
        f"/requirements/{rid}/subrequirements",
        _sub_body(u),
        headers=functional_headers,
    )
    assert predicates.is_status(sr, 201)
    sid = predicates.json_body(sr)["id"]

    lst = http.get(http_client, f"/requirements/{rid}/subrequirements", headers=functional_headers)
    assert predicates.is_status(lst, 200)
    assert any(x["id"] == sid for x in predicates.json_body(lst))

    one = http.get(http_client, f"/subrequirements/{sid}", headers=functional_headers)
    assert predicates.is_status(one, 200)
    assert predicates.json_body(one)["id"] == sid

    me = http.get(http_client, "/users/me", headers=functional_headers)
    assert predicates.is_status(me, 200)
    username = predicates.json_body(me)["username"]

    approved = http.patch_json(
        http_client,
        f"/subrequirements/{sid}",
        {"status": "approved"},
        headers=functional_headers,
    )
    assert predicates.is_status(approved, 200)
    sub_body = predicates.json_body(approved)
    assert sub_body["status"] == "approved"
    assert sub_body["approved_by"] == username
    assert sub_body["approved_at"] is not None


# Expected failure


def test_subrequirements_get_returns_404_for_missing_id(http_client, functional_headers) -> None:
    missing = 999_999_999
    r = http.get(http_client, f"/subrequirements/{missing}", headers=functional_headers)
    assert predicates.is_status(r, 404)


def test_subrequirements_create_returns_404_for_missing_parent(http_client, functional_headers) -> None:
    missing_parent = 999_999_999
    r = http.post_json(
        http_client,
        f"/requirements/{missing_parent}/subrequirements",
        _sub_body(uuid.uuid4().hex[:6]),
        headers=functional_headers,
    )
    assert predicates.is_status(r, 404)
