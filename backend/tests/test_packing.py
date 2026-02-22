"""Unit tests for the packing algorithm."""
import pytest
from app.packing import (
    BoxItem, PlacedBox, MaxRectsBSSF,
    pack_layer_2d, pack_3d_with_layers, expand_boxes,
    validate_no_overlap, validate_within_bounds
)


class TestMaxRects:
    """Tests for MaxRects algorithm."""

    def test_single_box_fits(self):
        """A single box that fits should be placed."""
        packer = MaxRectsBSSF(100, 100)
        result = packer.insert(50, 30)
        assert result is not None
        rect, rotated = result
        assert rect.x == 0
        assert rect.y == 0
        assert rect.width == 50
        assert rect.height == 30
        assert not rotated

    def test_box_too_large(self):
        """A box that is too large should not be placed."""
        packer = MaxRectsBSSF(100, 100)
        result = packer.insert(150, 150, allow_rotation=False)
        assert result is None

    def test_rotation_helps(self):
        """Rotation should help fit boxes."""
        packer = MaxRectsBSSF(100, 50)
        # 80x30 won't fit normally but 30x80 fits
        result = packer.insert(80, 30, allow_rotation=True)
        assert result is not None
        rect, rotated = result
        assert rotated
        assert rect.width == 30
        assert rect.height == 80

    def test_multiple_boxes(self):
        """Multiple boxes should be placed without overlap."""
        packer = MaxRectsBSSF(100, 100)
        results = []
        for _ in range(4):
            result = packer.insert(40, 40)
            if result:
                results.append(result)
        assert len(results) == 4


class TestPackLayer2D:
    """Tests for 2D layer packing."""

    def test_simple_packing(self):
        """Simple boxes should pack correctly."""
        boxes = [
            BoxItem("A", 30, 20, 10, True, 0),
            BoxItem("B", 30, 20, 10, True, 1),
        ]
        placed, remaining = pack_layer_2d(100, 50, boxes)
        assert len(placed) == 2
        assert len(remaining) == 0

    def test_overflow_handling(self):
        """Boxes that don't fit should be returned as remaining."""
        boxes = [
            BoxItem("A", 60, 60, 10, True, 0),
            BoxItem("B", 60, 60, 10, True, 1),
            BoxItem("C", 60, 60, 10, True, 2),
        ]
        placed, remaining = pack_layer_2d(100, 100, boxes)
        assert len(placed) == 1
        assert len(remaining) == 2


class TestPack3DWithLayers:
    """Tests for 3D layer-by-layer packing."""

    def test_stacking_disabled(self):
        """With stacking disabled, only layer 1 should be used."""
        boxes = [
            BoxItem("A", 40, 40, 30, True, 0),
            BoxItem("B", 40, 40, 30, True, 1),
            BoxItem("C", 40, 40, 30, True, 2),
            BoxItem("D", 40, 40, 30, True, 3),
        ]
        placed, remaining, layers = pack_3d_with_layers(
            100, 100, 100, boxes, max_layers=3, stacking_enabled=False
        )
        # All should be at z=0
        for p in placed:
            assert p.z == 0
            assert p.layer == 1
        assert len(layers) == 1

    def test_stacking_enabled_multiple_layers(self):
        """With stacking enabled, multiple layers should be used."""
        boxes = [
            BoxItem("A", 80, 80, 30, True, i) for i in range(6)
        ]
        placed, remaining, layers = pack_3d_with_layers(
            100, 100, 100, boxes, max_layers=3, stacking_enabled=True
        )
        # Should use multiple layers
        layer_indices = set(p.layer for p in placed)
        assert len(layer_indices) > 1

    def test_height_constraint(self):
        """Boxes should not exceed trailer height."""
        boxes = [
            BoxItem("A", 50, 50, 40, True, i) for i in range(10)
        ]
        placed, remaining, layers = pack_3d_with_layers(
            100, 100, 80, boxes, max_layers=3, stacking_enabled=True
        )
        # Verify all placements are within height
        for p in placed:
            assert p.z + p.h <= 80

    def test_max_three_layers(self):
        """Maximum 3 layers should be enforced."""
        boxes = [
            BoxItem("A", 90, 90, 20, True, i) for i in range(10)
        ]
        placed, remaining, layers = pack_3d_with_layers(
            100, 100, 200, boxes, max_layers=3, stacking_enabled=True
        )
        layer_indices = set(p.layer for p in placed)
        assert max(layer_indices) <= 3


class TestValidation:
    """Tests for validation functions."""

    def test_no_overlap_valid(self):
        """Non-overlapping boxes should pass validation."""
        placements = [
            PlacedBox("A", 0, 0, 0, 10, 10, 10, False, 1),
            PlacedBox("B", 20, 0, 0, 10, 10, 10, False, 1),
            PlacedBox("C", 0, 20, 0, 10, 10, 10, False, 1),
        ]
        assert validate_no_overlap(placements) is True

    def test_no_overlap_invalid(self):
        """Overlapping boxes should fail validation."""
        placements = [
            PlacedBox("A", 0, 0, 0, 20, 20, 20, False, 1),
            PlacedBox("B", 10, 10, 10, 20, 20, 20, False, 1),
        ]
        assert validate_no_overlap(placements) is False

    def test_within_bounds_valid(self):
        """Boxes within bounds should pass validation."""
        placements = [
            PlacedBox("A", 0, 0, 0, 10, 10, 10, False, 1),
            PlacedBox("B", 90, 90, 90, 10, 10, 10, False, 1),
        ]
        assert validate_within_bounds(placements, 100, 100, 100) is True

    def test_within_bounds_invalid(self):
        """Boxes outside bounds should fail validation."""
        placements = [
            PlacedBox("A", 95, 0, 0, 10, 10, 10, False, 1),
        ]
        assert validate_within_bounds(placements, 100, 100, 100) is False


class TestExpandBoxes:
    """Tests for box expansion."""

    def test_expansion(self):
        """Quantities should expand correctly."""
        boxes = [
            {"sku": "A", "length": 10, "width": 10, "height": 10, "quantity": 3},
            {"sku": "B", "length": 20, "width": 20, "height": 20, "quantity": 2},
        ]
        expanded = expand_boxes(boxes)
        assert len(expanded) == 5
        assert sum(1 for b in expanded if b.sku == "A") == 3
        assert sum(1 for b in expanded if b.sku == "B") == 2


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self):
        """Same input should always produce same output."""
        boxes = [
            BoxItem("A", 30, 25, 20, True, i) for i in range(5)
        ] + [
            BoxItem("B", 40, 35, 25, True, i + 5) for i in range(3)
        ]

        results = []
        for _ in range(3):
            placed, remaining, layers = pack_3d_with_layers(
                100, 100, 100, boxes.copy(), max_layers=3, stacking_enabled=True
            )
            result = [(p.sku, p.x, p.y, p.z, p.rotated) for p in placed]
            results.append(result)

        # All results should be identical
        assert results[0] == results[1] == results[2]
