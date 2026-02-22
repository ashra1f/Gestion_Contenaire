"""API integration tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Health check should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestOptimizeEndpoint:
    """Tests for optimization endpoint."""

    def test_simple_optimization(self):
        """Simple optimization request should succeed."""
        request = {
            "trailer": {"length": 200, "width": 150, "height": 150, "unit": "cm"},
            "boxes": [
                {"sku": "A", "length": 40, "width": 30, "height": 30, "quantity": 2, "rotation_allowed": True}
            ],
            "stacking": {"enabled": True, "max_layers": 3},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "fits" in data
        assert "stats" in data
        assert "layers" in data
        assert data["fits"] is True

    def test_units_conversion(self):
        """Meters should be converted to centimeters."""
        request = {
            "trailer": {"length": 2, "width": 1.5, "height": 1.5, "unit": "m"},
            "boxes": [
                {"sku": "A", "length": 0.4, "width": 0.3, "height": 0.3, "quantity": 2, "rotation_allowed": True}
            ],
            "stacking": {"enabled": True, "max_layers": 3},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        assert response.status_code == 200
        data = response.json()
        # Volume should be in cm³
        assert data["stats"]["trailer_volume"] == 200 * 150 * 150

    def test_impossible_fit(self):
        """Request with too many boxes should report unplaced items."""
        request = {
            "trailer": {"length": 100, "width": 100, "height": 100, "unit": "cm"},
            "boxes": [
                {"sku": "HUGE", "length": 80, "width": 80, "height": 80, "quantity": 5, "rotation_allowed": True}
            ],
            "stacking": {"enabled": True, "max_layers": 3},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["fits"] is False
        assert len(data["unplaced"]) > 0

    def test_box_too_large_error(self):
        """Box larger than trailer should return 400 error."""
        request = {
            "trailer": {"length": 100, "width": 100, "height": 100, "unit": "cm"},
            "boxes": [
                {"sku": "HUGE", "length": 150, "width": 150, "height": 150, "quantity": 1, "rotation_allowed": False}
            ],
            "stacking": {"enabled": True, "max_layers": 3},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        assert response.status_code == 400

    def test_stacking_disabled(self):
        """Stacking disabled should use only one layer."""
        request = {
            "trailer": {"length": 200, "width": 150, "height": 150, "unit": "cm"},
            "boxes": [
                {"sku": "A", "length": 40, "width": 30, "height": 30, "quantity": 10, "rotation_allowed": True}
            ],
            "stacking": {"enabled": False, "max_layers": 1},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["layers_used"] == 1
        # All placements should be at z=0
        for layer in data["layers"]:
            assert layer["z_base"] == 0

    def test_response_structure(self):
        """Response should have correct structure."""
        request = {
            "trailer": {"length": 200, "width": 150, "height": 150, "unit": "cm"},
            "boxes": [
                {"sku": "BOX-A", "length": 40, "width": 30, "height": 60, "quantity": 2, "rotation_allowed": True}
            ],
            "stacking": {"enabled": True, "max_layers": 3},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        data = response.json()

        # Check stats structure
        assert "trailer_volume" in data["stats"]
        assert "used_volume" in data["stats"]
        assert "fill_rate" in data["stats"]
        assert "total_boxes_placed" in data["stats"]
        assert "layers_used" in data["stats"]

        # Check layer structure
        for layer in data["layers"]:
            assert "layer_index" in layer
            assert "z_base" in layer
            assert "layer_height" in layer
            assert "placements" in layer

            for placement in layer["placements"]:
                assert "sku" in placement
                assert "x" in placement
                assert "y" in placement
                assert "z" in placement
                assert "l" in placement
                assert "w" in placement
                assert "h" in placement
                assert "rotated" in placement

    def test_empty_boxes_error(self):
        """Empty boxes list should return validation error."""
        request = {
            "trailer": {"length": 200, "width": 150, "height": 150, "unit": "cm"},
            "boxes": [],
            "stacking": {"enabled": True, "max_layers": 3},
            "global_rotation_allowed": True
        }
        response = client.post("/optimize", json=request)
        assert response.status_code == 422


class TestDemoEndpoints:
    """Tests for demo scenarios endpoints."""

    def test_get_demos(self):
        """Should return all demo scenarios."""
        response = client.get("/demos")
        assert response.status_code == 200
        data = response.json()
        assert "small" in data
        assert "medium" in data
        assert "impossible" in data

    def test_get_specific_demo(self):
        """Should return specific demo scenario."""
        response = client.get("/demos/small")
        assert response.status_code == 200
        data = response.json()
        assert "trailer" in data
        assert "boxes" in data

    def test_demo_not_found(self):
        """Unknown demo should return 404."""
        response = client.get("/demos/unknown")
        assert response.status_code == 404
