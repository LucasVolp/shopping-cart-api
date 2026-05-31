class TestCheckout:
    def test_creates_order_from_cart(self, client, sample_user, cart_with_item):
        response = client.post(
            f"/orders/checkout/{sample_user['id']}",
            json={"payment_method": "PIX"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == sample_user["id"]
        assert data["status"] == "PENDING"
        assert data["total_amount"] > 0

    def test_checkout_marks_cart_as_checked_out(self, client, sample_user, cart_with_item):
        """After checkout the active cart no longer has items — a new empty cart is returned."""
        client.post(f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"})
        cart = client.get(f"/cart/{sample_user['id']}").json()
        assert cart["items"] == []

    def test_checkout_decrements_product_stock(self, client, sample_user, sample_product, cart_with_item):
        """cart_with_item adds quantity=2; stock should decrease by 2 after checkout."""
        client.post(f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"})
        product = client.get(f"/products/{sample_product['id']}").json()
        assert product["quantity_available"] == sample_product["quantity_available"] - 2

    def test_checkout_fails_when_stock_is_insufficient(self, client, sample_user, sample_product):
        """Requesting more than the available stock should return 409."""
        client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 999},
        )
        response = client.post(
            f"/orders/checkout/{sample_user['id']}",
            json={"payment_method": "CREDIT_CARD"},
        )
        assert response.status_code == 409
        assert "Out of stock" in response.json()["detail"]

    def test_checkout_fails_for_empty_cart(self, client, sample_user):
        response = client.post(
            f"/orders/checkout/{sample_user['id']}",
            json={"payment_method": "PIX"},
        )
        assert response.status_code == 409

    def test_stock_is_not_partially_decremented_on_failure(
        self, client, sample_user, sample_product, product_payload
    ):
        """If one item is out of stock, no stock should be decremented for any item.

        This verifies the atomicity of the checkout transaction:
        either all stock decrements succeed or none are committed.
        """
        second_product = client.post(
            "/products/",
            json={**product_payload, "name": "Mouse", "quantity_available": 1},
        ).json()

        client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 1},
        )
        client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": second_product["id"], "quantity": 999},
        )

        client.post(f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"})

        refreshed = client.get(f"/products/{sample_product['id']}").json()
        assert refreshed["quantity_available"] == sample_product["quantity_available"]

    def test_second_checkout_fails_when_stock_is_exhausted(
        self, client, sample_user, product_payload, user_payload
    ):
        """When stock is 1 and two users each have it in their cart, only the first checkout succeeds.

        This validates the atomic SQL UPDATE logic: the second checkout finds
        quantity_available = 0, rowcount == 0, and returns 409.

        Note: this test runs sequentially to prove the atomic SQL logic is correct.
        True concurrent load testing requires a dedicated tool (e.g. Locust) running
        against the live server with a real connection pool.
        """
        limited_product = client.post(
            "/products/",
            json={**product_payload, "name": "Last Unit", "quantity_available": 1},
        ).json()

        second_user = client.post(
            "/users/", json={**user_payload, "email": "second@example.com"}
        ).json()

        for uid in [sample_user["id"], second_user["id"]]:
            client.post(
                f"/cart/{uid}/items",
                json={"product_id": limited_product["id"], "quantity": 1},
            )

        first = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        )
        second = client.post(
            f"/orders/checkout/{second_user['id']}", json={"payment_method": "PIX"}
        )

        assert first.status_code == 201
        assert second.status_code == 409


class TestListOrders:
    def test_returns_empty_list_for_new_user(self, client, sample_user):
        response = client.get(f"/orders/user/{sample_user['id']}")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_orders_for_user(self, client, sample_user, sample_product, product_payload):
        """DynamicArray correctly accumulates all orders for a user."""
        client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": sample_product["id"], "quantity": 1},
        )
        client.post(f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"})

        second_product = client.post(
            "/products/", json={**product_payload, "name": "Phone"}
        ).json()
        client.post(
            f"/cart/{sample_user['id']}/items",
            json={"product_id": second_product["id"], "quantity": 1},
        )
        client.post(f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"})

        response = client.get(f"/orders/user/{sample_user['id']}")
        assert len(response.json()) == 2


class TestGetOrderDetail:
    def test_returns_order_with_items_and_payment(self, client, sample_user, cart_with_item):
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        ).json()
        response = client.get(f"/orders/{order['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["payment"]["payment_method"] == "PIX"

    def test_order_item_snapshot_preserves_product_name(
        self, client, sample_user, sample_product, cart_with_item
    ):
        """The product name in the order item must remain unchanged even if the product is renamed."""
        original_name = sample_product["name"]
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        ).json()
        client.put(f"/products/{sample_product['id']}", json={"name": "Renamed Product"})

        detail = client.get(f"/orders/{order['id']}").json()
        assert detail["items"][0]["product_name"] == original_name

    def test_returns_404_for_unknown_order(self, client):
        assert client.get("/orders/00000000-0000-0000-0000-000000000000").status_code == 404
