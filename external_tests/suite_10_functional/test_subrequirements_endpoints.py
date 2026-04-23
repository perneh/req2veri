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


def test_subrequirements_create_list_get(http_client, functional_headers) -> None:
    pr = http.post_json(http_client, "/requirements", _req_body(), headers=functional_headers)
    assert predicates.is_status(pr, 201)
    rid = predicates.json_body(pr)["id"]

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
