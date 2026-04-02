def _setup(client, auth_headers):
    project_id = client.post("/projects/", json={"name": "P"}, headers=auth_headers).json()["project_id"]
    task_id = client.post(f"/projects/{project_id}/tasks", json={"title": "T"}, headers=auth_headers).json()["id"]
    return project_id, task_id


def test_add_and_list_comments(client, auth_headers):
    _, task_id = _setup(client, auth_headers)
    resp = client.post(f"/projects/tasks/{task_id}/comments", json={"content": "Hello!"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["content"] == "Hello!"

    list_resp = client.get(f"/projects/tasks/{task_id}/comments", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_delete_own_comment(client, auth_headers):
    _, task_id = _setup(client, auth_headers)
    comment_id = client.post(
        f"/projects/tasks/{task_id}/comments", json={"content": "bye"}, headers=auth_headers
    ).json()["id"]

    resp = client.delete(f"/projects/tasks/comments/{comment_id}", headers=auth_headers)
    assert resp.status_code == 204


def test_cannot_delete_others_comment(client, db, auth_headers, second_auth_headers):
    _, task_id = _setup(client, auth_headers)
    comment_id = client.post(
        f"/projects/tasks/{task_id}/comments", json={"content": "mine"}, headers=auth_headers
    ).json()["id"]

    resp = client.delete(f"/projects/tasks/comments/{comment_id}", headers=second_auth_headers)
    assert resp.status_code == 404


def test_comment_on_nonexistent_task(client, auth_headers):
    resp = client.post("/projects/tasks/9999/comments", json={"content": "x"}, headers=auth_headers)
    assert resp.status_code == 404
