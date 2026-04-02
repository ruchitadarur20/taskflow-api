from tests.conftest import create_role, register_user, login_user


def test_register_success(client, db):
    create_role(db)
    resp = register_user(client)
    assert resp.status_code == 200
    assert resp.json()["message"] == "User registered successfully"


def test_register_duplicate_email(client, db):
    create_role(db)
    register_user(client)
    resp = register_user(client)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_login_success(client, db):
    create_role(db)
    register_user(client)
    resp = client.post("/auth/login", data={"username": "test@example.com", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db):
    create_role(db)
    register_user(client)
    resp = client.post("/auth/login", data={"username": "test@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user(client, db):
    resp = client.post("/auth/login", data={"username": "nobody@example.com", "password": "x"})
    assert resp.status_code == 401


def test_refresh_token(client, db):
    create_role(db)
    register_user(client)
    login_resp = client.post("/auth/login", data={"username": "test@example.com", "password": "password123"})
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_logout(client, db):
    create_role(db)
    register_user(client)
    login_resp = client.post("/auth/login", data={"username": "test@example.com", "password": "password123"})
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 200

    # Token should be revoked now
    resp2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401
