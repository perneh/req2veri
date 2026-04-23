from support import dashboard, predicates


def test_dashboard_summary_shape(http_client, functional_headers) -> None:
    r = dashboard.fetch_summary(http_client, functional_headers)
    assert predicates.is_status(r, 200)
    body = predicates.json_body(r)
    for k in (
        "requirements_total",
        "subrequirements_total",
        "tests_total",
        "requirements_verified",
        "tests_passed",
        "tests_failed",
        "tests_not_run",
        "tests_blocked",
    ):
        assert k in body
        assert isinstance(body[k], int)
