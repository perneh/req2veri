from typing import Any

import httpx


def is_status(response: httpx.Response, code: int) -> bool:
    return response.status_code == code


def json_body(response: httpx.Response) -> Any:
    if not response.content:
        return None
    return response.json()
