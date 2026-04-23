"""Dashboard summary helpers."""

from collections.abc import Mapping

import httpx

from support import http


def fetch_summary(client: httpx.Client, headers: Mapping[str, str]) -> httpx.Response:
    return http.get(client, "/dashboard/summary", headers=headers)
