class TestCreateProduct:
    def test_creates_product_successfully(self, client, product_payload):
        response = client.post("/products/", json=product_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_payload["name"]
        assert data["price"] == product_payload["price"]
        assert data["quantity_available"] == product_payload["quantity_available"]

    def test_response_includes_nested_category(self, client, product_payload, sample_category):
        response = client.post("/products/", json=product_payload)
        assert response.json()["category"]["id"] == sample_category["id"]

    def test_rejects_negative_price(self, client, product_payload):
        response = client.post("/products/", json={**product_payload, "price": -1.0})
        assert response.status_code == 422

    def test_rejects_zero_price(self, client, product_payload):
        response = client.post("/products/", json={**product_payload, "price": 0})
        assert response.status_code == 422

    def test_rejects_negative_quantity(self, client, product_payload):
        response = client.post("/products/", json={**product_payload, "quantity_available": -1})
        assert response.status_code == 422

    def test_accepts_zero_quantity(self, client, product_payload):
        response = client.post("/products/", json={**product_payload, "quantity_available": 0})
        assert response.status_code == 201


class TestListProducts:
    def test_returns_empty_list_initially(self, client):
        """DynamicArray with no items converts to an empty list."""
        assert client.get("/products/").json() == []

    def test_returns_all_products_via_dynamic_array(self, client, product_payload):
        """Verifies DynamicArray correctly holds and returns all products."""
        client.post("/products/", json=product_payload)
        client.post("/products/", json={**product_payload, "name": "Phone"})
        response = client.get("/products/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetProduct:
    def test_returns_product_by_id(self, client, sample_product):
        response = client.get(f"/products/{sample_product['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == sample_product["id"]

    def test_returns_404_for_unknown_id(self, client):
        assert client.get("/products/00000000-0000-0000-0000-000000000000").status_code == 404


class TestUpdateProduct:
    def test_updates_price(self, client, sample_product):
        response = client.put(f"/products/{sample_product['id']}", json={"price": 1299.99})
        assert response.status_code == 200
        assert response.json()["price"] == 1299.99

    def test_updates_stock(self, client, sample_product):
        response = client.put(f"/products/{sample_product['id']}", json={"quantity_available": 50})
        assert response.json()["quantity_available"] == 50

    def test_rejects_negative_price_on_update(self, client, sample_product):
        assert client.put(
            f"/products/{sample_product['id']}", json={"price": -5}
        ).status_code == 422


class TestDeleteProduct:
    def test_deletes_product_successfully(self, client, sample_product):
        assert client.delete(f"/products/{sample_product['id']}").status_code == 204

    def test_deleted_product_is_not_found(self, client, sample_product):
        client.delete(f"/products/{sample_product['id']}")
        assert client.get(f"/products/{sample_product['id']}").status_code == 404
