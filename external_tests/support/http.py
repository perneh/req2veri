from collections.abc import Mapping

import httpx


def client(base_url: str, *, timeout: float = 30.0) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=timeout)


def get(
    client: httpx.Client,
    path: str,
    *,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    return client.get(path, headers=None if headers is None else dict(headers))


def post_json(
    client: httpx.Client,
    path: str,
    body: object,
    *,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    return client.post(path, json=body, headers=None if headers is None else dict(headers))


def post_form(
    client: httpx.Client,
    path: str,
    data: Mapping[str, str],
    *,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    return client.post(path, data=dict(data), headers=None if headers is None else dict(headers))


def patch_json(
    client: httpx.Client,
    path: str,
    body: object,
    *,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    return client.patch(path, json=body, headers=None if headers is None else dict(headers))


def put_json(
    client: httpx.Client,
    path: str,
    body: object,
    *,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    return client.put(path, json=body, headers=None if headers is None else dict(headers))
