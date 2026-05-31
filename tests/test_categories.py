class TestCreateCategory:
    def test_creates_category_successfully(self, client, category_payload):
        response = client.post("/categories/", json=category_payload)
        assert response.status_code == 201
        assert response.json()["name"] == category_payload["name"]

    def test_rejects_duplicate_name(self, client, category_payload):
        client.post("/categories/", json=category_payload)
        response = client.post("/categories/", json=category_payload)
        assert response.status_code == 409


class TestGetCategory:
    def test_returns_category_by_id(self, client, sample_category):
        response = client.get(f"/categories/{sample_category['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == sample_category["id"]

    def test_returns_404_for_unknown_id(self, client):
        response = client.get("/categories/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestListCategories:
    def test_returns_empty_list_initially(self, client):
        assert client.get("/categories/").json() == []

    def test_returns_all_created_categories(self, client):
        client.post("/categories/", json={"name": "A"})
        client.post("/categories/", json={"name": "B"})
        assert len(client.get("/categories/").json()) == 2


class TestUpdateCategory:
    def test_updates_name(self, client, sample_category):
        response = client.put(f"/categories/{sample_category['id']}", json={"name": "Updated"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_rejects_name_already_taken(self, client, sample_category):
        other = client.post("/categories/", json={"name": "Other"}).json()
        response = client.put(f"/categories/{other['id']}", json={"name": sample_category["name"]})
        assert response.status_code == 404


class TestDeleteCategory:
    def test_deletes_category_successfully(self, client, sample_category):
        assert client.delete(f"/categories/{sample_category['id']}").status_code == 204

    def test_deleted_category_is_not_found(self, client, sample_category):
        client.delete(f"/categories/{sample_category['id']}")
        assert client.get(f"/categories/{sample_category['id']}").status_code == 404
