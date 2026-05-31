class TestGetPaymentByOrder:
    def test_returns_payment_for_existing_order(self, client, sample_user, cart_with_item):
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        ).json()
        response = client.get(f"/payments/order/{order['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order["id"]
        assert data["payment_method"] == "PIX"
        assert data["payment_status"] == "PENDING"

    def test_payment_total_matches_order_total(self, client, sample_user, cart_with_item):
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        ).json()
        payment = client.get(f"/payments/order/{order['id']}").json()
        assert payment["total_amount"] == order["total_amount"]

    def test_returns_404_for_unknown_order(self, client):
        response = client.get("/payments/order/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestUpdatePaymentStatus:
    def test_updates_status_to_completed(self, client, sample_user, cart_with_item):
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        ).json()
        payment = client.get(f"/payments/order/{order['id']}").json()

        response = client.patch(
            f"/payments/{payment['id']}/status",
            json={"payment_status": "COMPLETED"},
        )
        assert response.status_code == 200
        assert response.json()["payment_status"] == "COMPLETED"

    def test_updates_status_to_failed(self, client, sample_user, cart_with_item):
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "CREDIT_CARD"}
        ).json()
        payment = client.get(f"/payments/order/{order['id']}").json()

        response = client.patch(
            f"/payments/{payment['id']}/status",
            json={"payment_status": "FAILED"},
        )
        assert response.json()["payment_status"] == "FAILED"

    def test_returns_404_for_unknown_payment(self, client):
        response = client.patch(
            "/payments/00000000-0000-0000-0000-000000000000/status",
            json={"payment_status": "COMPLETED"},
        )
        assert response.status_code == 404

    def test_rejects_invalid_status_value(self, client, sample_user, cart_with_item):
        order = client.post(
            f"/orders/checkout/{sample_user['id']}", json={"payment_method": "PIX"}
        ).json()
        payment = client.get(f"/payments/order/{order['id']}").json()

        response = client.patch(
            f"/payments/{payment['id']}/status",
            json={"payment_status": "INVALID_STATUS"},
        )
        assert response.status_code == 422
