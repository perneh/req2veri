from tests.helpers import register_and_token, register_and_token_as


def test_public_health_and_logs_endpoints(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    r = client.get("/logs")
    assert r.status_code == 200
    assert "path" in r.json()
    assert isinstance(r.json()["lines"], list)


def test_requirement_crud(client):
    token = register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/requirements",
        headers=headers,
        json={
            "key": "REQ-100",
            "title": "T",
            "description": "D",
            "status": "draft",
            "priority": "low",
        },
    )
    assert r.status_code == 201
    rid = r.json()["id"]
    assert r.json()["updated_by"] == "u1"
    assert r.json()["updated_at"]

    r = client.get("/requirements", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get(f"/requirements/{rid}/coverage", headers=headers)
    assert r.status_code == 200
    assert r.json()["tests_total"] == 0

    r = client.post(
        f"/requirements/{rid}/tests",
        headers=headers,
        json={
            "key": "TEST-900",
            "title": "VT",
            "description": "",
            "precondition": "",
            "action": "Execute step 1",
            "method": "test",
            "requirement_id": rid,
            "sub_requirement_id": None,
            "expected_result": "x",
        },
    )
    assert r.status_code == 201
    assert r.json()["status"] == "not_run"
    assert r.json()["actual_result"] == ""
    assert r.json()["updated_by"] == "u1"
    assert r.json()["updated_at"]

    r = client.get(f"/requirements/{rid}/coverage", headers=headers)
    assert r.json()["tests_total"] == 1


def test_standalone_test_and_reference_filter(client):
    token = register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/tests",
        headers=headers,
        json={
            "key": "ST-1",
            "title": "Standalone",
            "description": "",
            "precondition": "None",
            "action": "Run procedure A",
            "method": "analysis",
            "requirement_id": None,
            "sub_requirement_id": None,
            "expected_result": "",
        },
    )
    assert r.status_code == 201
    assert r.json()["requirement_id"] is None
    assert r.json()["sub_requirement_id"] is None
    assert r.json()["status"] == "not_run"
    assert r.json()["actual_result"] == ""
    assert r.json()["precondition"] == "None"
    assert r.json()["action"] == "Run procedure A"
    assert r.json()["updated_by"] == "u1"
    assert r.json()["updated_at"]

    r = client.get("/tests?reference=unlinked", headers=headers)
    assert r.status_code == 200
    assert {x["key"] for x in r.json()} == {"ST-1"}
    assert all(x["requirement_id"] is None and x["sub_requirement_id"] is None for x in r.json())

    r = client.post(
        "/requirements",
        headers=headers,
        json={
            "key": "REQ-LINK",
            "title": "For linked filter",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
    )
    assert r.status_code == 201
    rid = r.json()["id"]
    r = client.post(
        f"/requirements/{rid}/tests",
        headers=headers,
        json={
            "key": "LINK-T",
            "title": "Linked",
            "description": "",
            "method": "test",
            "requirement_id": rid,
            "sub_requirement_id": None,
            "expected_result": "",
        },
    )
    assert r.status_code == 201

    r = client.get("/tests?reference=linked", headers=headers)
    assert r.status_code == 200
    assert {x["key"] for x in r.json()} == {"LINK-T"}
    assert all(x["requirement_id"] is not None or x["sub_requirement_id"] is not None for x in r.json())


def test_admin_backup_database_basic_auth_and_sqlite_file(client):
    from pathlib import Path

    r = client.post("/admin/backup-database", auth=("reset-admin", "wrong"))
    assert r.status_code == 401

    r = client.post("/admin/backup-database", auth=("reset-admin", "reset-test-password"))
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["format"] == "sqlite_copy"
    assert data["bytes"] > 0

    name = Path(data["path"]).name
    assert Path(data["path"]).is_file()

    r_del_bad = client.delete(f"/admin/backups/{name}", auth=("reset-admin", "wrong"))
    assert r_del_bad.status_code == 401

    r_del = client.delete(f"/admin/backups/{name}", auth=("reset-admin", "reset-test-password"))
    assert r_del.status_code == 204
    assert not Path(data["path"]).is_file()

    r_again = client.delete(f"/admin/backups/{name}", auth=("reset-admin", "reset-test-password"))
    assert r_again.status_code == 404

    r_bad_name = client.delete("/admin/backups/evil.txt", auth=("reset-admin", "reset-test-password"))
    assert r_bad_name.status_code == 400


def test_admin_reset_database_password_protected(client):
    token = register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/requirements",
        headers=headers,
        json={
            "key": "REQ-RESET-1",
            "title": "Before reset",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
    )
    assert r.status_code == 201

    r = client.post("/admin/reset-database", auth=("reset-admin", "wrong"))
    assert r.status_code == 401

    r = client.post("/admin/reset-database", auth=("reset-admin", "reset-test-password"))
    assert r.status_code == 200
    assert r.json()["ok"] is True

    # Old token user is gone after full DB reset; register a fresh user.
    token2 = register_and_token(client)
    r = client.get("/requirements", headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200
    assert r.json() == []


def test_users_list_requires_auth_and_returns_registered_users(client):
    r = client.get("/users")
    assert r.status_code == 401

    token = register_and_token(client)
    r = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    users = r.json()
    assert any(u["username"] == "u1" for u in users)


def test_updated_by_and_updated_at_for_req_sub_and_test(client):
    token_u1 = register_and_token_as(client, "u1a")
    token_u2 = register_and_token_as(client, "u2a")
    h1 = {"Authorization": f"Bearer {token_u1}"}
    h2 = {"Authorization": f"Bearer {token_u2}"}

    rr = client.post(
        "/requirements",
        headers=h1,
        json={
            "key": "REQ-AUD-1",
            "title": "Audit",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
    )
    assert rr.status_code == 201
    rid = rr.json()["id"]
    assert rr.json()["updated_by"] == "u1a"
    assert rr.json()["updated_at"]

    sr = client.post(
        f"/requirements/{rid}/subrequirements",
        headers=h1,
        json={
            "key": "REQ-AUD-1.1",
            "title": "Sub audit",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
    )
    assert sr.status_code == 201
    sid = sr.json()["id"]
    assert sr.json()["updated_by"] == "u1a"
    assert sr.json()["updated_at"]

    tr = client.post(
        f"/subrequirements/{sid}/tests",
        headers=h1,
        json={
            "key": "TEST-AUD-1",
            "title": "Test audit",
            "description": "",
            "precondition": "",
            "action": "",
            "method": "test",
            "requirement_id": None,
            "sub_requirement_id": sid,
            "expected_result": "",
        },
    )
    assert tr.status_code == 201
    tid = tr.json()["id"]
    assert tr.json()["updated_by"] == "u1a"
    assert tr.json()["updated_at"]

    rr2 = client.patch(f"/requirements/{rid}", headers=h2, json={"title": "Audit updated"})
    assert rr2.status_code == 200
    assert rr2.json()["updated_by"] == "u2a"
    assert rr2.json()["updated_at"]

    sr2 = client.patch(f"/subrequirements/{sid}", headers=h2, json={"title": "Sub updated"})
    assert sr2.status_code == 200
    assert sr2.json()["updated_by"] == "u2a"
    assert sr2.json()["updated_at"]

    tr2 = client.patch(f"/tests/{tid}", headers=h2, json={"title": "Test updated"})
    assert tr2.status_code == 200
    assert tr2.json()["updated_by"] == "u2a"
    assert tr2.json()["updated_at"]


def test_entity_history_list_restore_delete(client):
    token = register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    rr = client.post(
        "/requirements",
        headers=headers,
        json={
            "key": "REQ-HIST-1",
            "title": "Original title",
            "description": "D",
            "status": "draft",
            "priority": "low",
        },
    )
    assert rr.status_code == 201
    rid = rr.json()["id"]

    h0 = client.get(f"/requirements/{rid}/history", headers=headers)
    assert h0.status_code == 200
    assert len(h0.json()) == 1
    assert h0.json()[0]["version"] == 1

    client.patch(f"/requirements/{rid}", headers=headers, json={"title": "Edited title"})
    h1 = client.get(f"/requirements/{rid}/history", headers=headers)
    assert h1.status_code == 200
    assert len(h1.json()) == 2
    by_v = {x["version"]: x["id"] for x in h1.json()}
    hid_v1 = by_v[1]
    detail = client.get(f"/requirements/{rid}/history/{hid_v1}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["snapshot"]["title"] == "Original title"

    rest = client.post(f"/requirements/{rid}/history/{hid_v1}/restore", headers=headers)
    assert rest.status_code == 200
    assert rest.json()["title"] == "Original title"

    h2 = client.get(f"/requirements/{rid}/history", headers=headers)
    assert len(h2.json()) == 3
    hid_v2 = next(x["id"] for x in h2.json() if x["version"] == 2)
    dl = client.delete(f"/requirements/{rid}/history/{hid_v2}", headers=headers)
    assert dl.status_code == 204
    h3 = client.get(f"/requirements/{rid}/history", headers=headers)
    assert len(h3.json()) == 2

    sr = client.post(
        f"/requirements/{rid}/subrequirements",
        headers=headers,
        json={
            "key": "REQ-HIST-1.1",
            "title": "Sub orig",
            "description": "",
            "status": "draft",
            "priority": "low",
        },
    )
    assert sr.status_code == 201
    sid = sr.json()["id"]
    assert len(client.get(f"/subrequirements/{sid}/history", headers=headers).json()) == 1
    client.patch(f"/subrequirements/{sid}", headers=headers, json={"title": "Sub new"})
    sh = client.get(f"/subrequirements/{sid}/history", headers=headers)
    assert len(sh.json()) == 2
    sub_hid = next(x["id"] for x in sh.json() if x["version"] == 1)
    assert (
        client.get(f"/subrequirements/{sid}/history/{sub_hid}", headers=headers).json()["snapshot"]["title"]
        == "Sub orig"
    )
    assert client.post(f"/subrequirements/{sid}/history/{sub_hid}/restore", headers=headers).status_code == 200
    assert client.delete(f"/subrequirements/{sid}/history/{sub_hid}", headers=headers).status_code == 204

    tr = client.post(
        "/tests",
        headers=headers,
        json={
            "key": "TEST-HIST-1",
            "title": "Test orig",
            "description": "",
            "precondition": "",
            "action": "",
            "method": "test",
            "requirement_id": None,
            "sub_requirement_id": None,
            "expected_result": "",
        },
    )
    assert tr.status_code == 201
    tid = tr.json()["id"]
    assert len(client.get(f"/tests/{tid}/history", headers=headers).json()) == 1
    client.patch(f"/tests/{tid}", headers=headers, json={"title": "Test new"})
    th = client.get(f"/tests/{tid}/history", headers=headers)
    thid = next(x["id"] for x in th.json() if x["version"] == 1)
    assert client.get(f"/tests/{tid}/history/{thid}", headers=headers).json()["snapshot"]["title"] == "Test orig"
    assert client.post(f"/tests/{tid}/history/{thid}/restore", headers=headers).status_code == 200
    assert client.delete(f"/tests/{tid}/history/{thid}", headers=headers).status_code == 204
