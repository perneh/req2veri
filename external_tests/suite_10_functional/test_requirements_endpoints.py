import uuid

from support import auth, http, predicates


def _req_body(key_suffix: str) -> dict:
    u = uuid.uuid4().hex[:8]
    return {
        "key": f"F{u}{key_suffix}"[:32],
        "title": "Functional requirement",
        "description": "",
        "status": "draft",
        "priority": "low",
    }


def test_requirements_list_get_post_patch(http_client, functional_headers) -> None:
    created = http.post_json(
        http_client,
        "/requirements",
        _req_body("A"),
        headers=functional_headers,
    )
    assert predicates.is_status(created, 201)
    rid = predicates.json_body(created)["id"]

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
