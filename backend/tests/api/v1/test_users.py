from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"email": "test_create@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_create@example.com"
    assert "id" in data
    assert "is_active" in data


def test_create_user_duplicate_email(client: TestClient):
    client.post(
        "/api/v1/users/",
        json={"email": "test_duplicate@example.com", "password": "password123"},
    )
    response = client.post(
        "/api/v1/users/",
        json={"email": "test_duplicate@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_read_users(client: TestClient):
    client.post(
        "/api/v1/users/",
        json={"email": "user1@example.com", "password": "password123"},
    )
    client.post(
        "/api/v1/users/",
        json={"email": "user2@example.com", "password": "password123"},
    )
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_read_user(client: TestClient):
    create_res = client.post(
        "/api/v1/users/",
        json={"email": "test_read@example.com", "password": "password123"},
    )
    user_id = create_res.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test_read@example.com"


def test_read_user_not_found(client: TestClient):
    response = client.get("/api/v1/users/999999")
    assert response.status_code == 404
