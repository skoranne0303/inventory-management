import pytest


class TestRestockingEndpoints:

    def test_get_empty_restocking_orders(self, client):
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_restocking_order(self, client):
        payload = {
            "items": [
                {"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 150, "unit_cost": 18.50},
                {"sku": "FLT-405", "name": "Oil Filter Cartridge", "quantity": 100, "unit_cost": 8.99}
            ],
            "total_cost": 3674.00
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "Processing"
        assert data["lead_time_days"] == 7
        assert len(data["items"]) == 2
        assert data["total_cost"] == 3674.00

    def test_create_order_appears_in_list(self, client):
        payload = {
            "items": [{"sku": "GSK-203", "name": "High-Temperature Gasket", "quantity": 50, "unit_cost": 12.75}],
            "total_cost": 637.50
        }
        client.post("/api/restocking/orders", json=payload)
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        orders = response.json()
        assert any(o["total_cost"] == 637.50 for o in orders)

    def test_create_order_invalid_empty_items(self, client):
        payload = {"items": [], "total_cost": 0.0}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 400

    def test_order_number_format(self, client):
        payload = {
            "items": [{"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 10, "unit_cost": 18.50}],
            "total_cost": 185.00
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["order_number"].startswith("RST-")

    def test_order_has_7_day_lead_time(self, client):
        from datetime import datetime, timedelta
        payload = {
            "items": [{"sku": "FLT-405", "name": "Oil Filter Cartridge", "quantity": 50, "unit_cost": 8.99}],
            "total_cost": 449.50
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["lead_time_days"] == 7
        order_date = datetime.fromisoformat(data["order_date"])
        expected = datetime.fromisoformat(data["expected_delivery"])
        assert (expected - order_date).days == 7

    def test_order_response_has_required_fields(self, client):
        payload = {
            "items": [{"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 5, "unit_cost": 18.50}],
            "total_cost": 92.50
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201
        data = response.json()
        for field in ("id", "order_number", "status", "order_date", "expected_delivery", "items", "total_cost", "lead_time_days"):
            assert field in data
