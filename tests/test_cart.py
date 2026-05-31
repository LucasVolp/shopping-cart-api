class TestGetCart:
    def test_creates_cart_automatically_when_none_exists(self, client, sample_user):
        """Getting a cart for a user with no cart should create one on the fly."""
        response = client.get(f"/cart/{sample_user['id']}")
        assert response.status_code == 200
        assert response.json()["user_id"] == sample_user["id"]
        assert response.json()["items"] == []

    def test_returns_existing_cart(self, client, cart_with_item):
        assert len(cart_with_item["items"]) == 1


class TestAddCartItem:
    def test_adds_item_to_cart(self, client, sample_user, sample_product):
        response = client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 3},
        )
        assert response.status_code == 201
        assert len(response.json()["items"]) == 1
        assert response.json()["items"][0]["quantity"] == 3

    def test_increments_quantity_for_existing_product(self, client, sample_user, sample_product):
        """Adding the same product twice should increment quantity, not create a duplicate."""
        client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 2},
        )
        response = client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 3},
        )
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["quantity"] == 5

    def test_rejects_zero_quantity(self, client, sample_user, sample_product):
        response = client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 0},
        )
        assert response.status_code == 422

    def test_rejects_negative_quantity(self, client, sample_user, sample_product):
        response = client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": -1},
        )
        assert response.status_code == 422


class TestUpdateCartItem:
    def test_updates_item_quantity(self, client, sample_user, cart_with_item):
        item_id = cart_with_item["items"][0]["id"]
        response = client.patch(
            f"/cart/{sample_user['id']}/items/{item_id}",
            json={"quantity": 9},
        )
        assert response.status_code == 200
        assert response.json()["items"][0]["quantity"] == 9

    def test_returns_404_for_item_not_in_user_cart(self, client, sample_user):
        response = client.patch(
            f"/cart/{sample_user['id']}/items/00000000-0000-0000-0000-000000000000",
            json={"quantity": 1},
        )
        assert response.status_code == 404


class TestRemoveCartItem:
    def test_removes_item_from_cart(self, client, sample_user, cart_with_item):
        item_id = cart_with_item["items"][0]["id"]
        response = client.delete(f"/cart/{sample_user['id']}/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["items"] == []

    def test_returns_404_for_unknown_item(self, client, sample_user):
        response = client.delete(
            f"/cart/{sample_user['id']}/items/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404


class TestClearCart:
    def test_clears_all_items(self, client, sample_user, cart_with_item):
        response = client.delete(f"/cart/{sample_user['id']}/items")
        assert response.status_code == 200
        assert response.json()["items"] == []

    def test_clear_on_empty_cart_returns_empty_cart(self, client, sample_user):
        response = client.delete(f"/cart/{sample_user['id']}/items")
        assert response.status_code == 200
        assert response.json()["items"] == []
