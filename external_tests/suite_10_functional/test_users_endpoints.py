from support import auth, http, predicates


def test_users_me_returns_current_user(http_client, functional_headers) -> None:
    r = http.get(http_client, "/users/me", headers=functional_headers)
    assert predicates.is_status(r, 200)
    body = predicates.json_body(r)
    assert "username" in body
    assert "email" in body
