import uuid

from support import http, predicates


def _create_version(http_client, functional_headers) -> int:
    key = f"ext-{uuid.uuid4().hex[:16]}"
    created = http.post_json(
        http_client,
        "/test-object-versions",
        {"key": key, "name": "External version", "description": ""},
        headers=functional_headers,
    )
    assert predicates.is_status(created, 201)
    return predicates.json_body(created)["id"]


# Expected success


def test_test_object_versions_list_and_create(http_client, functional_headers) -> None:
    before = http.get(http_client, "/test-object-versions", headers=functional_headers)
    assert predicates.is_status(before, 200)

    vid = _create_version(http_client, functional_headers)

    after = http.get(http_client, "/test-object-versions", headers=functional_headers)
    assert predicates.is_status(after, 200)
    assert any(v["id"] == vid for v in predicates.json_body(after))


# Expected failure


def test_test_object_versions_create_returns_409_for_duplicate_key(http_client, functional_headers) -> None:
    key = f"ext-{uuid.uuid4().hex[:16]}"
    body = {"key": key, "name": "External version", "description": ""}
    first = http.post_json(http_client, "/test-object-versions", body, headers=functional_headers)
    assert predicates.is_status(first, 201)
    second = http.post_json(http_client, "/test-object-versions", body, headers=functional_headers)
    assert predicates.is_status(second, 409)


def test_version_runs_returns_404_for_missing_version(http_client, functional_headers) -> None:
    missing = 999_999_999
    r = http.get(http_client, f"/test-object-versions/{missing}/runs", headers=functional_headers)
    assert predicates.is_status(r, 404)
