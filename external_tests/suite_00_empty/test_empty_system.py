"""
Assumes **no business data** in the database: zero requirements, sub-requirements,
and verification tests (fresh DB or wiped tables). Users may already exist.

If this fails after seed/demo data, use an empty instance or truncate those tables.
"""

import os

from support import auth, dashboard, flow, http, predicates


def test_health_public(http_client) -> None:
    r = http.get(http_client, "/health")
    assert predicates.is_status(r, 200)
    assert predicates.json_body(r) == {"status": "ok"}


def test_dashboard_global_counts_are_zero(http_client) -> None:
    def fresh_session() -> tuple[str, dict[str, str]]:
        t = flow.register_and_token(http_client)
        return t, auth.bearer_headers(t)

    def purge_business_data(headers: dict[str, str]) -> None:
        # Remove all requirements (cascades sub-requirements and linked tests).
        # Repeat because list is paginated and shrinks while deleting.
        while True:
            reqs = http.get(http_client, "/requirements?limit=500", headers=headers)
            assert predicates.is_status(reqs, 200), reqs.text
            rows = predicates.json_body(reqs)
            if not rows:
                break
            for row in rows:
                dr = http_client.delete(f"/requirements/{row['id']}", headers=headers)
                assert predicates.is_status(dr, 204), dr.text

        # Remove any remaining standalone tests.
        while True:
            tests = http.get(http_client, "/tests?limit=500", headers=headers)
            assert predicates.is_status(tests, 200), tests.text
            rows = predicates.json_body(tests)
            if not rows:
                break
            for row in rows:
                dt = http_client.delete(f"/tests/{row['id']}", headers=headers)
                assert predicates.is_status(dt, 204), dt.text

    _, headers = fresh_session()
    r = dashboard.fetch_summary(http_client, headers)
    assert predicates.is_status(r, 200), r.text
    body = predicates.json_body(r)

    # If non-empty, first try admin reset; if disabled, purge through normal APIs.
    if body["requirements_total"] != 0 or body["subrequirements_total"] != 0 or body["tests_total"] != 0:
        reset_user = os.environ.get("REQ2VERI_RESET_DB_USER") or os.environ.get("RESET_DB_USER")
        reset_password = os.environ.get("REQ2VERI_RESET_DB_PASSWORD") or os.environ.get("RESET_DB_PASSWORD")
        if reset_user and reset_password:
            rr = http_client.post("/admin/reset-database", auth=(reset_user, reset_password))
            if rr.status_code == 200:
                # Reset deletes users too; refresh auth session.
                _, headers = fresh_session()
            elif rr.status_code == 503:
                purge_business_data(headers)
            else:
                raise AssertionError(rr.text)
        else:
            purge_business_data(headers)

        r = dashboard.fetch_summary(http_client, headers)
        assert predicates.is_status(r, 200), r.text
        body = predicates.json_body(r)

    assert body["requirements_total"] == 0
    assert body["subrequirements_total"] == 0
    assert body["tests_total"] == 0
