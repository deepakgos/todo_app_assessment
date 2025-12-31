import json
import pytest
from todo_app.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_create_task(client):
    response = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Test Task"}),
        content_type="application/json"
    )
    assert response.status_code == 201
    assert "id" in response.get_json()


def test_get_tasks(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_task_by_id(client):
    create_response = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Single Task"}),
        content_type="application/json"
    )
    assert create_response.status_code == 201

    task_id = create_response.get_json()["id"]

    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200


def test_delete_task(client):
    create_response = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Delete Task"}),
        content_type="application/json"
    )

    task_id = create_response.get_json()["id"]

    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
