from tests.conftest import create_role, register_user, login_user


def _setup_project(client, auth_headers):
    resp = client.post("/projects/", json={"name": "Test Project"}, headers=auth_headers)
    return resp.json()["project_id"]


def _create_task(client, auth_headers, project_id, title="Fix bug", due_date=None):
    payload = {"title": title}
    if due_date:
        payload["due_date"] = due_date
    return client.post(f"/projects/{project_id}/tasks", json=payload, headers=auth_headers)


def test_create_task(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    resp = _create_task(client, auth_headers, project_id)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Fix bug"
    assert data["status"] == "todo"
    assert data["project_id"] == project_id


def test_create_task_with_due_date(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    resp = _create_task(client, auth_headers, project_id, due_date="2026-12-31T23:59:00Z")
    assert resp.status_code == 200
    assert resp.json()["due_date"] is not None


def test_list_tasks(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    _create_task(client, auth_headers, project_id, "Task A")
    _create_task(client, auth_headers, project_id, "Task B")
    resp = client.get(f"/projects/{project_id}/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_filter_tasks_by_status(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    task_resp = _create_task(client, auth_headers, project_id)
    task_id = task_resp.json()["id"]

    client.put(f"/projects/tasks/{task_id}/status", json={"status": "in_progress"}, headers=auth_headers)

    resp = client.get(f"/projects/{project_id}/tasks?task_status=in_progress", headers=auth_headers)
    assert resp.status_code == 200
    assert all(t["status"] == "in_progress" for t in resp.json())


def test_update_task_status(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    task_id = _create_task(client, auth_headers, project_id).json()["id"]

    resp = client.put(f"/projects/tasks/{task_id}/status", json={"status": "done"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["new_status"] == "done"


def test_update_task_status_invalid(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    task_id = _create_task(client, auth_headers, project_id).json()["id"]

    resp = client.put(f"/projects/tasks/{task_id}/status", json={"status": "invalid_status"}, headers=auth_headers)
    assert resp.status_code == 422


def test_delete_task(client, auth_headers):
    project_id = _setup_project(client, auth_headers)
    task_id = _create_task(client, auth_headers, project_id).json()["id"]

    resp = client.delete(f"/projects/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200

    tasks = client.get(f"/projects/{project_id}/tasks", headers=auth_headers).json()
    assert all(t["id"] != task_id for t in tasks)


def test_create_task_on_nonexistent_project(client, auth_headers):
    resp = client.post("/projects/9999/tasks", json={"title": "Ghost"}, headers=auth_headers)
    assert resp.status_code == 404


def test_non_member_cannot_create_task(client, db, auth_headers, second_auth_headers):
    project_id = _setup_project(client, auth_headers)
    resp = _create_task(client, second_auth_headers, project_id)
    assert resp.status_code == 403
