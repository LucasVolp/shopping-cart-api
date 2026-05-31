import pytest


class TestCreateUser:
    def test_creates_user_successfully(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_payload["email"]
        assert data["name"] == user_payload["name"]

    def test_never_exposes_password(self, client, user_payload):
        response = client.post("/users/", json=user_payload)
        assert "password" not in response.json()

    def test_rejects_duplicate_email(self, client, user_payload):
        client.post("/users/", json=user_payload)
        response = client.post("/users/", json=user_payload)
        assert response.status_code == 409

    def test_rejects_invalid_email_format(self, client):
        response = client.post("/users/", json={"name": "A", "email": "not-an-email", "password": "123"})
        assert response.status_code == 422


class TestGetUser:
    def test_returns_user_by_id(self, client, sample_user):
        response = client.get(f"/users/{sample_user['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == sample_user["id"]

    def test_returns_404_for_unknown_id(self, client):
        response = client.get("/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_returns_user_with_empty_orders(self, client, sample_user):
        response = client.get(f"/users/{sample_user['id']}/details")
        assert response.status_code == 200
        assert response.json()["orders"] == []


class TestListUsers:
    def test_returns_empty_list_initially(self, client):
        response = client.get("/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_created_users(self, client, user_payload):
        client.post("/users/", json=user_payload)
        client.post("/users/", json={**user_payload, "email": "other@example.com"})
        response = client.get("/users/")
        assert len(response.json()) == 2


class TestUpdateUser:
    def test_updates_name(self, client, sample_user):
        response = client.put(f"/users/{sample_user['id']}", json={"name": "Updated Name"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_rejects_email_already_taken(self, client, sample_user, user_payload):
        other = client.post("/users/", json={**user_payload, "email": "other@example.com"}).json()
        response = client.put(f"/users/{other['id']}", json={"email": sample_user["email"]})
        assert response.status_code == 409

    def test_returns_404_for_unknown_id(self, client):
        response = client.put("/users/00000000-0000-0000-0000-000000000000", json={"name": "X"})
        assert response.status_code == 404


class TestDeleteUser:
    def test_deletes_user_successfully(self, client, sample_user):
        response = client.delete(f"/users/{sample_user['id']}")
        assert response.status_code == 204

    def test_deleted_user_is_not_found(self, client, sample_user):
        client.delete(f"/users/{sample_user['id']}")
        response = client.get(f"/users/{sample_user['id']}")
        assert response.status_code == 404

    def test_returns_404_for_unknown_id(self, client):
        response = client.delete("/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
