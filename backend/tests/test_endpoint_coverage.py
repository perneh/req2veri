"""Positive and negative functional tests across backend HTTP endpoints."""

from __future__ import annotations

import os
from unittest import mock

from fastapi.testclient import TestClient

from tests.helpers import auth_header, register_and_token, register_user


# --- Public ---


def test_health_positive(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_logs_positive_and_validation_negative(client: TestClient):
    r = client.get("/logs")
    assert r.status_code == 200
    assert "lines" in r.json()

    r2 = client.get("/logs?lines=0")
    assert r2.status_code == 422

    r3 = client.get("/logs?lines=201")
    assert r3.status_code == 422


# --- Auth ---


def test_register_positive_and_duplicate_negative(client: TestClient):
    r = client.post(
        "/auth/register",
        json={"username": "reg1", "email": "reg1@example.com", "password": "pw12345678"},
    )
    assert r.status_code == 201
    assert r.json()["username"] == "reg1"

    r2 = client.post(
        "/auth/register",
        json={"username": "reg1", "email": "other@example.com", "password": "pw12345678"},
    )
    assert r2.status_code == 409
    assert "username" in r2.json()["detail"].lower()

    r3 = client.post(
        "/auth/register",
        json={"username": "reg2", "email": "reg1@example.com", "password": "pw12345678"},
    )
    assert r3.status_code == 409
    assert "email" in r3.json()["detail"].lower()


def test_register_invalid_body_negative(client: TestClient):
    r = client.post("/auth/register", json={"username": "x", "email": "not-an-email", "password": "pw12345678"})
    assert r.status_code == 422


def test_token_positive_and_wrong_password_negative(client: TestClient):
    register_user(client, "tokuser", email="tokuser@example.com")
    r = client.post("/auth/token", data={"username": "tokuser", "password": "pw12345678"})
    assert r.status_code == 200
    assert "access_token" in r.json()

    r2 = client.post("/auth/token", data={"username": "tokuser", "password": "wrongpassword"})
    assert r2.status_code == 401

    r3 = client.post("/auth/token", data={"username": "nobody_xyz", "password": "pw12345678"})
    assert r3.status_code == 401


# --- Bearer auth ---


def test_protected_routes_require_bearer_negative(client: TestClient):
    assert client.get("/users/me").status_code == 401
    assert client.get("/users/me", headers={"Authorization": "Basic x"}).status_code == 401
    assert client.get("/users/me", headers={"Authorization": "Bearer invalid-token"}).status_code == 401


def test_users_me_positive(client: TestClient):
    token = register_and_token(client, "meuser", email="meuser@example.com")
    r = client.get("/users/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["username"] == "meuser"


def test_users_list_positive(client: TestClient):
    token = register_and_token(client, "listu", email="listu@example.com")
    r = client.get("/users", headers=auth_header(token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert any(u["username"] == "listu" for u in r.json())


# --- Dashboard ---


def test_dashboard_summary_positive_and_unauth_negative(client: TestClient):
    assert client.get("/dashboard/summary").status_code == 401
    token = register_and_token(client, "dashu", email="dashu@example.com")
    r = client.get("/dashboard/summary", headers=auth_header(token))
    assert r.status_code == 200
    body = r.json()
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


# --- Test object versions ---


def _minimal_test_json(key: str, *, req_id: int | None = None, sub_id: int | None = None):
    return {
        "key": key,
        "title": "t",
        "description": "",
        "precondition": "",
        "action": "",
        "method": "test",
        "requirement_id": req_id,
        "sub_requirement_id": sub_id,
        "expected_result": "",
    }


def test_test_object_versions_positive_and_conflicts_negative(client: TestClient):
    token = register_and_token(client, "veruser", email="veruser@example.com")
    h = auth_header(token)

    assert client.get("/test-object-versions", headers=h).status_code == 200

    r = client.post("/test-object-versions", headers=h, json={"key": "v1.0", "name": "N", "description": ""})
    assert r.status_code == 201
    vid = r.json()["id"]

    r_dup = client.post("/test-object-versions", headers=h, json={"key": "v1.0", "name": "Other", "description": ""})
    assert r_dup.status_code == 409

    r404 = client.get("/test-object-versions/99999/runs", headers=h)
    assert r404.status_code == 404

    rr = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-V", "title": "T", "description": "", "status": "draft", "priority": "low"},
    )
    assert rr.status_code == 201
    rid = rr.json()["id"]
    tr = client.post(f"/requirements/{rid}/tests", headers=h, json=_minimal_test_json("TEST-V", req_id=rid))
    assert tr.status_code == 201
    tid = tr.json()["id"]

    r_run = client.post(
        f"/test-object-versions/{vid}/runs",
        headers=h,
        json={"verification_test_id": tid, "status": "not_run", "expected_result": "", "actual_result": ""},
    )
    assert r_run.status_code == 201

    r_run_404v = client.post(
        "/test-object-versions/99999/runs",
        headers=h,
        json={"verification_test_id": tid, "status": "not_run", "expected_result": "", "actual_result": ""},
    )
    assert r_run_404v.status_code == 404

    r_run_404t = client.post(
        f"/test-object-versions/{vid}/runs",
        headers=h,
        json={"verification_test_id": 99999, "status": "not_run", "expected_result": "", "actual_result": ""},
    )
    assert r_run_404t.status_code == 404

    r_list = client.get(f"/test-object-versions/{vid}/runs", headers=h)
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1


# --- Requirements CRUD + 404/409 ---


def test_requirements_get_patch_delete_positive_and_not_found_negative(client: TestClient):
    token = register_and_token(client, "requser", email="requser@example.com")
    h = auth_header(token)

    assert client.get("/requirements/99999", headers=h).status_code == 404

    r = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-COV-1", "title": "T1", "description": "", "status": "draft", "priority": "low"},
    )
    assert r.status_code == 201
    rid = r.json()["id"]

    g = client.get(f"/requirements/{rid}", headers=h)
    assert g.status_code == 200
    assert g.json()["key"] == "REQ-COV-1"

    p = client.patch(f"/requirements/{rid}", headers=h, json={"title": "T1b"})
    assert p.status_code == 200
    assert p.json()["title"] == "T1b"

    assert client.patch("/requirements/99999", headers=h, json={"title": "x"}).status_code == 404

    d = client.delete(f"/requirements/{rid}", headers=h)
    assert d.status_code == 204
    assert client.get(f"/requirements/{rid}", headers=h).status_code == 404
    assert client.delete(f"/requirements/{rid}", headers=h).status_code == 404


def test_requirement_duplicate_key_negative(client: TestClient):
    token = register_and_token(client, "dupreq", email="dupreq@example.com")
    h = auth_header(token)
    body = {"key": "REQ-DUP", "title": "A", "description": "", "status": "draft", "priority": "low"}
    assert client.post("/requirements", headers=h, json=body).status_code == 201
    r2 = client.post("/requirements", headers=h, json=body)
    assert r2.status_code == 409


def test_requirement_patch_key_conflict_negative(client: TestClient):
    token = register_and_token(client, "keyc", email="keyc@example.com")
    h = auth_header(token)
    client.post("/requirements", headers=h, json={"key": "REQ-KA", "title": "A", "description": "", "status": "draft", "priority": "low"})
    r_b = client.post(
        "/requirements", headers=h, json={"key": "REQ-KB", "title": "B", "description": "", "status": "draft", "priority": "low"}
    )
    bid = r_b.json()["id"]
    r_conflict = client.patch(f"/requirements/{bid}", headers=h, json={"key": "REQ-KA"})
    assert r_conflict.status_code == 409


def test_requirements_list_query_and_limit_validation(client: TestClient):
    token = register_and_token(client, "listq", email="listq@example.com")
    h = auth_header(token)
    client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-Q1", "title": "Alpha search", "description": "", "status": "draft", "priority": "high"},
    )
    r = client.get("/requirements?q=Alpha", headers=h)
    assert r.status_code == 200
    assert len(r.json()) >= 1

    r2 = client.get("/requirements?status=draft&priority=high", headers=h)
    assert r2.status_code == 200

    assert client.get("/requirements?limit=501", headers=h).status_code == 422


def test_requirements_hierarchy_positive(client: TestClient):
    token = register_and_token(client, "hieru", email="hieru@example.com")
    h = auth_header(token)
    rid = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-H", "title": "H", "description": "", "status": "draft", "priority": "low"},
    ).json()["id"]
    client.post(
        f"/requirements/{rid}/subrequirements",
        headers=h,
        json={"key": "REQ-H.1", "title": "S", "description": "", "status": "draft", "priority": "low"},
    )
    r = client.get("/requirements/hierarchy", headers=h)
    assert r.status_code == 200
    assert len(r.json()) >= 1
    item = next(x for x in r.json() if x["requirement"]["key"] == "REQ-H")
    assert len(item["sub_requirements"]) >= 1


def test_requirement_sub_tests_coverage_traceability_positive_and_404(client: TestClient):
    token = register_and_token(client, "traceu", email="traceu@example.com")
    h = auth_header(token)
    rid = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-TR", "title": "T", "description": "", "status": "draft", "priority": "low"},
    ).json()["id"]

    assert client.get(f"/requirements/{rid}/subrequirements", headers=h).status_code == 200
    assert client.get("/requirements/99999/subrequirements", headers=h).status_code == 404

    sr = client.post(
        f"/requirements/{rid}/subrequirements",
        headers=h,
        json={"key": "REQ-TR.1", "title": "Sub", "description": "", "status": "draft", "priority": "low"},
    )
    assert sr.status_code == 201
    sid = sr.json()["id"]

    tr = client.post(f"/requirements/{rid}/tests", headers=h, json=_minimal_test_json("REQ-TR-T", req_id=rid))
    assert tr.status_code == 201

    cov = client.get(f"/requirements/{rid}/coverage", headers=h)
    assert cov.status_code == 200
    assert cov.json()["tests_total"] >= 1

    assert client.get("/requirements/99999/coverage", headers=h).status_code == 404

    trc = client.get(f"/requirements/{rid}/traceability", headers=h)
    assert trc.status_code == 200
    assert "requirement" in trc.json()
    assert client.get("/requirements/99999/traceability", headers=h).status_code == 404

    dup_sub = client.post(
        f"/requirements/{rid}/subrequirements",
        headers=h,
        json={"key": "REQ-TR.1", "title": "Dup", "description": "", "status": "draft", "priority": "low"},
    )
    assert dup_sub.status_code == 409


def test_requirement_history_404_negative(client: TestClient):
    token = register_and_token(client, "hist404", email="hist404@example.com")
    h = auth_header(token)
    assert client.get("/requirements/99999/history", headers=h).status_code == 404
    assert client.get("/requirements/99999/history/1", headers=h).status_code == 404

    rid = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-H404", "title": "T", "description": "", "status": "draft", "priority": "low"},
    ).json()["id"]
    assert client.get(f"/requirements/{rid}/history/99999", headers=h).status_code == 404


def test_requirement_create_validation_negative(client: TestClient):
    token = register_and_token(client, "valu", email="valu@example.com")
    h = auth_header(token)
    r = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-MISS", "description": "", "status": "draft", "priority": "low"},
    )
    assert r.status_code == 422


# --- Sub-requirements ---


def test_subrequirement_crud_and_404_negative(client: TestClient):
    token = register_and_token(client, "subu", email="subu@example.com")
    h = auth_header(token)
    rid = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-SUB", "title": "R", "description": "", "status": "draft", "priority": "low"},
    ).json()["id"]
    sr = client.post(
        f"/requirements/{rid}/subrequirements",
        headers=h,
        json={"key": "REQ-SUB.1", "title": "S", "description": "", "status": "draft", "priority": "low"},
    )
    assert sr.status_code == 201
    sid = sr.json()["id"]

    assert client.get(f"/subrequirements/{sid}", headers=h).status_code == 200
    assert client.get("/subrequirements/99999", headers=h).status_code == 404

    assert client.patch(f"/subrequirements/{sid}", headers=h, json={"title": "S2"}).status_code == 200
    assert client.patch("/subrequirements/99999", headers=h, json={"title": "x"}).status_code == 404

    assert client.get(f"/subrequirements/{sid}/tests", headers=h).status_code == 200
    assert client.get("/subrequirements/99999/tests", headers=h).status_code == 404

    d = client.delete(f"/subrequirements/{sid}", headers=h)
    assert d.status_code == 204
    assert client.get(f"/subrequirements/{sid}", headers=h).status_code == 404


def test_subrequirement_history_wrong_id_negative(client: TestClient):
    token = register_and_token(client, "sh404", email="sh404@example.com")
    h = auth_header(token)
    rid = client.post(
        "/requirements",
        headers=h,
        json={"key": "REQ-SH", "title": "R", "description": "", "status": "draft", "priority": "low"},
    ).json()["id"]
    sid = client.post(
        f"/requirements/{rid}/subrequirements",
        headers=h,
        json={"key": "REQ-SH.1", "title": "S", "description": "", "status": "draft", "priority": "low"},
    ).json()["id"]
    assert client.get(f"/subrequirements/{sid}/history/99999", headers=h).status_code == 404


# --- Tests resource ---


def test_tests_list_get_patch_delete_and_validation_negative(client: TestClient):
    token = register_and_token(client, "testu", email="testu@example.com")
    h = auth_header(token)

    assert client.get("/tests?reference=invalid", headers=h).status_code == 422

    r = client.post("/tests", headers=h, json=_minimal_test_json("TEST-LIST", req_id=None, sub_id=None))
    assert r.status_code == 201
    tid = r.json()["id"]

    assert client.get(f"/tests/{tid}", headers=h).status_code == 200
    assert client.get("/tests/99999", headers=h).status_code == 404

    assert client.get("/tests?reference=any", headers=h).status_code == 200

    assert client.patch(f"/tests/{tid}", headers=h, json={"title": "new"}).status_code == 200
    assert client.patch("/tests/99999", headers=h, json={"title": "x"}).status_code == 404

    bad = client.patch(
        f"/tests/{tid}",
        headers=h,
        json={"requirement_id": 1, "sub_requirement_id": 1},
    )
    assert bad.status_code == 422

    missing_req = client.patch(
        f"/tests/{tid}",
        headers=h,
        json={"requirement_id": 99999, "sub_requirement_id": None},
    )
    assert missing_req.status_code == 404

    d = client.delete(f"/tests/{tid}", headers=h)
    assert d.status_code == 204
    assert client.get(f"/tests/{tid}", headers=h).status_code == 404


def test_test_duplicate_key_negative(client: TestClient):
    token = register_and_token(client, "testdup", email="testdup@example.com")
    h = auth_header(token)
    assert client.post("/tests", headers=h, json=_minimal_test_json("TD-K", req_id=None, sub_id=None)).status_code == 201
    r2 = client.post("/tests", headers=h, json=_minimal_test_json("TD-K", req_id=None, sub_id=None))
    assert r2.status_code == 409


def test_tests_list_limit_validation_negative(client: TestClient):
    token = register_and_token(client, "limu", email="limu@example.com")
    assert client.get("/tests?limit=501", headers=auth_header(token)).status_code == 422


def test_verification_test_history_404_negative(client: TestClient):
    token = register_and_token(client, "vh404", email="vh404@example.com")
    h = auth_header(token)
    tid = client.post("/tests", headers=h, json=_minimal_test_json("VH-T", req_id=None, sub_id=None)).json()["id"]
    assert client.get(f"/tests/{tid}/history/99999", headers=h).status_code == 404


# --- Admin: disabled credentials ---


def test_admin_endpoints_503_when_reset_credentials_unset(client: TestClient):
    from app.config import get_settings

    get_settings.cache_clear()
    try:
        with mock.patch.dict(os.environ, {"RESET_DB_USER": "", "RESET_DB_PASSWORD": ""}):
            get_settings.cache_clear()
            r_reset = client.post("/admin/reset-database", auth=("reset-admin", "reset-test-password"))
            assert r_reset.status_code == 503
            r_bak = client.post("/admin/backup-database", auth=("reset-admin", "reset-test-password"))
            assert r_bak.status_code == 503
            r_del = client.delete("/admin/backups/req2veri_sqlite_20200101_000000.db", auth=("reset-admin", "reset-test-password"))
            assert r_del.status_code == 503
    finally:
        get_settings.cache_clear()
        with mock.patch.dict(
            os.environ,
            {"RESET_DB_USER": "reset-admin", "RESET_DB_PASSWORD": "reset-test-password"},
        ):
            get_settings.cache_clear()
