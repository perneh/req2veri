import uuid

from support import http, predicates


def test_test_object_versions_list_and_create(http_client, functional_headers) -> None:
    before = http.get(http_client, "/test-object-versions", headers=functional_headers)
    assert predicates.is_status(before, 200)

    key = f"ext-{uuid.uuid4().hex[:16]}"
    created = http.post_json(
        http_client,
        "/test-object-versions",
        {"key": key, "name": "External version", "description": ""},
        headers=functional_headers,
    )
    assert predicates.is_status(created, 201)
    vid = predicates.json_body(created)["id"]

    after = http.get(http_client, "/test-object-versions", headers=functional_headers)
    assert predicates.is_status(after, 200)
    assert any(v["id"] == vid for v in predicates.json_body(after))
