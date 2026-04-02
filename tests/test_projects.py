from tests.conftest import create_role, register_user, login_user


def _create_project(client, headers, name="My Project", description="A project"):
    return client.post("/projects/", json={"name": name, "description": description}, headers=headers)


def test_create_project(client, auth_headers):
    resp = _create_project(client, auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "My Project"
    assert "project_id" in data


def test_list_my_projects(client, auth_headers):
    _create_project(client, auth_headers, name="P1")
    _create_project(client, auth_headers, name="P2")
    resp = client.get("/projects/my-projects", headers=auth_headers)
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "P1" in names
    assert "P2" in names


def test_create_project_unauthenticated(client):
    resp = client.post("/projects/", json={"name": "X"})
    assert resp.status_code == 401


def test_add_member(client, db, auth_headers, second_auth_headers):
    project_resp = _create_project(client, auth_headers)
    project_id = project_resp.json()["project_id"]

    # Get second user's id
    me_resp = client.get("/users/me", headers=second_auth_headers)
    second_user_id = me_resp.json()["id"]

    resp = client.post(
        f"/projects/{project_id}/members",
        json={"user_id": second_user_id, "role_id": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] == second_user_id


def test_add_member_non_owner_forbidden(client, db, auth_headers, second_auth_headers):
    project_resp = _create_project(client, auth_headers)
    project_id = project_resp.json()["project_id"]

    me_resp = client.get("/users/me", headers=auth_headers)
    owner_id = me_resp.json()["id"]

    resp = client.post(
        f"/projects/{project_id}/members",
        json={"user_id": owner_id, "role_id": 1},
        headers=second_auth_headers,
    )
    assert resp.status_code == 403
