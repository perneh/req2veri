import uuid

from support import http, predicates


def _req_body(key_suffix: str) -> dict:
    u = uuid.uuid4().hex[:8]
    return {
        "key": f"F{u}{key_suffix}"[:32],
        "title": "Functional requirement",
        "description": "",
        "status": "draft",
        "priority": "low",
    }


def _create_requirement(http_client, functional_headers) -> int:
    created = http.post_json(
        http_client,
        "/requirements",
        _req_body("A"),
        headers=functional_headers,
    )
    assert predicates.is_status(created, 201)
    return predicates.json_body(created)["id"]


# Expected success


def test_requirements_list_get_post_patch(http_client, functional_headers) -> None:
    rid = _create_requirement(http_client, functional_headers)

    one = http.get(http_client, f"/requirements/{rid}", headers=functional_headers)
    assert predicates.is_status(one, 200)
    assert predicates.json_body(one)["id"] == rid

    listed = http.get(http_client, "/requirements", headers=functional_headers)
    assert predicates.is_status(listed, 200)
    assert any(x["id"] == rid for x in predicates.json_body(listed))

    patched = http.patch_json(
        http_client,
        f"/requirements/{rid}",
        {"title": "Updated title"},
        headers=functional_headers,
    )
    assert predicates.is_status(patched, 200)
    assert predicates.json_body(patched)["title"] == "Updated title"


# Expected failure


def test_requirements_get_returns_404_for_missing_id(http_client, functional_headers) -> None:
    missing = 999_999_999
    r = http.get(http_client, f"/requirements/{missing}", headers=functional_headers)
    assert predicates.is_status(r, 404)


def test_requirements_post_returns_409_for_duplicate_key(http_client, functional_headers) -> None:
    body = _req_body("DUP")
    first = http.post_json(http_client, "/requirements", body, headers=functional_headers)
    assert predicates.is_status(first, 201)
    second = http.post_json(http_client, "/requirements", body, headers=functional_headers)
    assert predicates.is_status(second, 409)
