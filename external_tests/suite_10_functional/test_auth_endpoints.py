from support import auth, predicates


# Expected success

def test_register_returns_201(http_client) -> None:
    password = "ExtPw12345678!"
    username = auth.unique_username()
    r = auth.register(http_client, auth.register_payload(username=username, password=password))
    assert predicates.is_status(r, 201)


def test_token_returns_200_with_valid_password(http_client) -> None:
    password = "ExtPw12345678!"
    username = auth.unique_username()
    auth.register(http_client, auth.register_payload(username=username, password=password))
    r = auth.token(http_client, username=username, password=password)
    assert predicates.is_status(r, 200)
    assert auth.access_token(r)


# Expected failure

def test_token_returns_401_with_bad_password(http_client) -> None:
    password = "ExtPw12345678!"
    username = auth.unique_username()
    auth.register(http_client, auth.register_payload(username=username, password=password))
    r = auth.token(http_client, username=username, password=password + "x")
    assert predicates.is_status(r, 401)


def test_register_returns_409_for_duplicate_username(http_client) -> None:
    password = "ExtPw12345678!"
    username = auth.unique_username()
    payload = auth.register_payload(username=username, password=password)
    first = auth.register(http_client, payload)
    assert predicates.is_status(first, 201)

    second = auth.register(http_client, payload)
    assert predicates.is_status(second, 409)
