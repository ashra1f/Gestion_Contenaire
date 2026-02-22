"""
3D Bin Packing Algorithm using MaxRects heuristic.
Implements layer-by-layer packing with optional stacking.
"""
from typing import List, Tuple, Optional
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class Rect:
    """A 2D rectangle for MaxRects algorithm."""
    x: float
    y: float
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height

    def contains(self, other: 'Rect') -> bool:
        """Check if this rect fully contains another."""
        return (other.x >= self.x and
                other.y >= self.y and
                other.x + other.width <= self.x + self.width and
                other.y + other.height <= self.y + self.height)

    def intersects(self, other: 'Rect') -> bool:
        """Check if this rect intersects with another."""
        return not (other.x >= self.x + self.width or
                    other.x + other.width <= self.x or
                    other.y >= self.y + self.height or
                    other.y + other.height <= self.y)


@dataclass
class BoxItem:
    """A box to be placed."""
    sku: str
    length: float
    width: float
    height: float
    rotation_allowed: bool
    original_index: int  # For deterministic ordering

    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass
class PlacedBox:
    """A placed box with position and orientation."""
    sku: str
    x: float
    y: float
    z: float
    l: float
    w: float
    h: float
    rotated: bool
    layer: int


class MaxRectsBSSF:
    """
    MaxRects Best Short Side Fit algorithm for 2D bin packing.
    This is a well-known heuristic that maintains a list of free rectangles.
    """

    def __init__(self, width: float, height: float):
        self.bin_width = width
        self.bin_height = height
        self.free_rects: List[Rect] = [Rect(0, 0, width, height)]
        self.used_rects: List[Rect] = []

    def insert(self, width: float, height: float, allow_rotation: bool = True
               ) -> Optional[Tuple[Rect, bool]]:
        """
        Try to insert a rectangle. Returns (placed_rect, rotated) or None if it doesn't fit.
        Uses Best Short Side Fit heuristic.
        """
        best_rect = None
        best_short_side = float('inf')
        best_long_side = float('inf')
        best_rotated = False
        best_index = -1

        for i, free_rect in enumerate(self.free_rects):
            # Try without rotation
            if width <= free_rect.width and height <= free_rect.height:
                leftover_h = abs(free_rect.width - width)
                leftover_v = abs(free_rect.height - height)
                short_side = min(leftover_h, leftover_v)
                long_side = max(leftover_h, leftover_v)

                if short_side < best_short_side or \
                   (short_side == best_short_side and long_side < best_long_side):
                    best_rect = Rect(free_rect.x, free_rect.y, width, height)
                    best_short_side = short_side
                    best_long_side = long_side
                    best_rotated = False
                    best_index = i

            # Try with rotation
            if allow_rotation and height <= free_rect.width and width <= free_rect.height:
                leftover_h = abs(free_rect.width - height)
                leftover_v = abs(free_rect.height - width)
                short_side = min(leftover_h, leftover_v)
                long_side = max(leftover_h, leftover_v)

                if short_side < best_short_side or \
                   (short_side == best_short_side and long_side < best_long_side):
                    best_rect = Rect(free_rect.x, free_rect.y, height, width)
                    best_short_side = short_side
                    best_long_side = long_side
                    best_rotated = True
                    best_index = i

        if best_rect is None:
            return None

        # Place the rectangle
        self._place_rect(best_rect)
        return (best_rect, best_rotated)

    def _place_rect(self, rect: Rect):
        """Place a rectangle and update free rectangles."""
        self.used_rects.append(rect)

        # Split free rectangles
        new_free_rects = []
        for free_rect in self.free_rects:
            if not rect.intersects(free_rect):
                new_free_rects.append(free_rect)
            else:
                # Generate new free rectangles from the split
                # Right part
                if rect.x + rect.width < free_rect.x + free_rect.width:
                    new_rect = Rect(
                        rect.x + rect.width,
                        free_rect.y,
                        free_rect.x + free_rect.width - rect.x - rect.width,
                        free_rect.height
                    )
                    new_free_rects.append(new_rect)

                # Left part
                if rect.x > free_rect.x:
                    new_rect = Rect(
                        free_rect.x,
                        free_rect.y,
                        rect.x - free_rect.x,
                        free_rect.height
                    )
                    new_free_rects.append(new_rect)

                # Top part
                if rect.y + rect.height < free_rect.y + free_rect.height:
                    new_rect = Rect(
                        free_rect.x,
                        rect.y + rect.height,
                        free_rect.width,
                        free_rect.y + free_rect.height - rect.y - rect.height
                    )
                    new_free_rects.append(new_rect)

                # Bottom part
                if rect.y > free_rect.y:
                    new_rect = Rect(
                        free_rect.x,
                        free_rect.y,
                        free_rect.width,
                        rect.y - free_rect.y
                    )
                    new_free_rects.append(new_rect)

        self.free_rects = new_free_rects
        self._prune_free_rects()

    def _prune_free_rects(self):
        """Remove redundant free rectangles (those contained by others)."""
        pruned = []
        for i, rect_a in enumerate(self.free_rects):
            is_contained = False
            for j, rect_b in enumerate(self.free_rects):
                if i != j and rect_b.contains(rect_a):
                    is_contained = True
                    break
            if not is_contained:
                pruned.append(rect_a)
        self.free_rects = pruned


def pack_layer_2d(
    trailer_l: float,
    trailer_w: float,
    boxes: List[BoxItem]
) -> Tuple[List[Tuple[BoxItem, float, float, bool]], List[BoxItem]]:
    """
    Pack boxes into a single 2D layer using MaxRects algorithm.

    Args:
        trailer_l: Trailer length (x-axis)
        trailer_w: Trailer width (y-axis)
        boxes: List of boxes to place

    Returns:
        Tuple of (placed_boxes_with_positions, remaining_boxes)
        Each placed box is (BoxItem, x, y, rotated)
    """
    packer = MaxRectsBSSF(trailer_l, trailer_w)
    placed: List[Tuple[BoxItem, float, float, bool]] = []
    remaining: List[BoxItem] = []

    for box in boxes:
        result = packer.insert(box.length, box.width, box.rotation_allowed)
        if result:
            rect, rotated = result
            placed.append((box, rect.x, rect.y, rotated))
        else:
            remaining.append(box)

    return placed, remaining


def pack_3d_with_layers(
    trailer_l: float,
    trailer_w: float,
    trailer_h: float,
    boxes: List[BoxItem],
    max_layers: int = 3,
    stacking_enabled: bool = True
) -> Tuple[List[PlacedBox], List[BoxItem], List[Tuple[int, float, float]]]:
    """
    Pack boxes into a 3D trailer using layer-by-layer approach.

    Args:
        trailer_l, trailer_w, trailer_h: Trailer dimensions
        boxes: List of boxes to place
        max_layers: Maximum number of layers (1-3)
        stacking_enabled: Whether stacking is enabled

    Returns:
        Tuple of (placed_boxes, remaining_boxes, layer_info)
        layer_info is list of (layer_index, z_base, layer_height)
    """
    if not stacking_enabled:
        max_layers = 1

    # Sort boxes by volume descending for better packing
    # Use original_index as tiebreaker for determinism
    sorted_boxes = sorted(
        boxes,
        key=lambda b: (-b.volume(), b.original_index)
    )

    placed_boxes: List[PlacedBox] = []
    remaining_boxes = sorted_boxes.copy()
    layer_info: List[Tuple[int, float, float]] = []

    current_z = 0.0

    for layer_idx in range(1, max_layers + 1):
        if not remaining_boxes:
            break

        # Filter boxes that can fit in remaining height
        available_height = trailer_h - current_z
        if available_height <= 0:
            break

        # Try to place boxes in this layer
        boxes_for_layer = [b for b in remaining_boxes if b.height <= available_height]
        if not boxes_for_layer:
            break

        layer_placed, still_remaining = pack_layer_2d(
            trailer_l, trailer_w, boxes_for_layer
        )

        if not layer_placed:
            break

        # Calculate layer height (max height of placed boxes)
        layer_height = max(
            box.height if not rotated else box.height
            for box, _, _, rotated in layer_placed
        )

        # Record layer info
        layer_info.append((layer_idx, current_z, layer_height))

        # Add placed boxes
        for box, x, y, rotated in layer_placed:
            l = box.width if rotated else box.length
            w = box.length if rotated else box.width
            placed_boxes.append(PlacedBox(
                sku=box.sku,
                x=x,
                y=y,
                z=current_z,
                l=l,
                w=w,
                h=box.height,
                rotated=rotated,
                layer=layer_idx
            ))

        # Update remaining boxes
        placed_skus_indices = {(b.sku, b.original_index) for b, _, _, _ in layer_placed}
        remaining_boxes = [
            b for b in remaining_boxes
            if (b.sku, b.original_index) not in placed_skus_indices
        ]

        # Move to next layer
        current_z += layer_height

    return placed_boxes, remaining_boxes, layer_info


def expand_boxes(boxes_with_qty: List[dict]) -> List[BoxItem]:
    """
    Expand boxes with quantities into individual BoxItem instances.

    Args:
        boxes_with_qty: List of box definitions with quantities

    Returns:
        List of individual BoxItem instances
    """
    expanded = []
    idx = 0
    for box_def in boxes_with_qty:
        for _ in range(box_def['quantity']):
            expanded.append(BoxItem(
                sku=box_def['sku'],
                length=box_def['length'],
                width=box_def['width'],
                height=box_def['height'],
                rotation_allowed=box_def.get('rotation_allowed', True),
                original_index=idx
            ))
            idx += 1
    return expanded


def validate_no_overlap(placements: List[PlacedBox]) -> bool:
    """Check that no placed boxes overlap."""
    for i, p1 in enumerate(placements):
        for j, p2 in enumerate(placements):
            if i >= j:
                continue
            # Check 3D overlap
            x_overlap = (p1.x < p2.x + p2.l) and (p2.x < p1.x + p1.l)
            y_overlap = (p1.y < p2.y + p2.w) and (p2.y < p1.y + p1.w)
            z_overlap = (p1.z < p2.z + p2.h) and (p2.z < p1.z + p1.h)
            if x_overlap and y_overlap and z_overlap:
                return False
    return True


def validate_within_bounds(
    placements: List[PlacedBox],
    trailer_l: float,
    trailer_w: float,
    trailer_h: float
) -> bool:
    """Check that all placed boxes are within trailer bounds."""
    for p in placements:
        if p.x < 0 or p.y < 0 or p.z < 0:
            return False
        if p.x + p.l > trailer_l + 0.001:  # Small epsilon for float comparison
            return False
        if p.y + p.w > trailer_w + 0.001:
            return False
        if p.z + p.h > trailer_h + 0.001:
            return False
    return True
