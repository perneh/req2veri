def _register_and_token(client):
    client.post(
        "/auth/register",
        json={"username": "u1", "email": "u1@example.com", "password": "pw12345678"},
    )
    r = client.post("/auth/token", data={"username": "u1", "password": "pw12345678"})
    assert r.status_code == 200
    return r.json()["access_token"]


def _register_and_token_as(client, username: str):
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "pw12345678"},
    )
    r = client.post("/auth/token", data={"username": username, "password": "pw12345678"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_requirement_crud(client):
    token = _register_and_token(client)
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
    token = _register_and_token(client)
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


def test_admin_reset_database_password_protected(client):
    token = _register_and_token(client)
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
    token2 = _register_and_token(client)
    r = client.get("/requirements", headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200
    assert r.json() == []


def test_users_list_requires_auth_and_returns_registered_users(client):
    r = client.get("/users")
    assert r.status_code == 401

    token = _register_and_token(client)
    r = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    users = r.json()
    assert any(u["username"] == "u1" for u in users)


def test_updated_by_and_updated_at_for_req_sub_and_test(client):
    token_u1 = _register_and_token_as(client, "u1a")
    token_u2 = _register_and_token_as(client, "u2a")
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
