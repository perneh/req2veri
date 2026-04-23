from support import http, predicates


# Expected success

def test_users_me_returns_current_user(http_client, functional_headers) -> None:
    r = http.get(http_client, "/users/me", headers=functional_headers)
    assert predicates.is_status(r, 200)
    body = predicates.json_body(r)
    assert "username" in body
    assert "email" in body


def test_users_list_returns_200_for_authenticated_user(http_client, functional_headers) -> None:
    r = http.get(http_client, "/users", headers=functional_headers)
    assert predicates.is_status(r, 200)
    assert isinstance(predicates.json_body(r), list)


# Expected failure

def test_users_me_returns_401_without_token(http_client) -> None:
    r = http.get(http_client, "/users/me")
    assert predicates.is_status(r, 401)
