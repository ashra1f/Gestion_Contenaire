"""
FastAPI application for Trailer Loading Optimizer.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from collections import defaultdict

from .models import (
    OptimizeRequest, OptimizeResponse, Trailer, Box, Unit,
    Placement, Layer, UnplacedItem, Stats
)
from .packing import (
    expand_boxes, pack_3d_with_layers, BoxItem, PlacedBox,
    validate_no_overlap, validate_within_bounds
)

app = FastAPI(
    title="Trailer Loading Optimizer",
    description="API for optimizing cargo placement in trailers with 3D bin packing",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_loading(request: OptimizeRequest) -> OptimizeResponse:
    """
    Optimize cargo placement in trailer.

    Returns placement solution with 3D coordinates and statistics.
    """
    # Convert to cm
    trailer = request.trailer.to_cm()
    boxes = [box.to_cm(request.trailer.unit) for box in request.boxes]

    # Validate boxes fit individually
    for box in boxes:
        fits_normal = (
            box.length <= trailer.length and
            box.width <= trailer.width and
            box.height <= trailer.height
        )
        fits_rotated = (
            box.rotation_allowed and
            box.width <= trailer.length and
            box.length <= trailer.width and
            box.height <= trailer.height
        )
        if not fits_normal and not fits_rotated:
            raise HTTPException(
                status_code=400,
                detail=f"Box '{box.sku}' ({box.length}x{box.width}x{box.height}) "
                       f"is too large for trailer ({trailer.length}x{trailer.width}x{trailer.height})"
            )

    # Prepare boxes for packing
    boxes_dict = [
        {
            'sku': box.sku,
            'length': box.length,
            'width': box.width,
            'height': box.height,
            'quantity': box.quantity,
            'rotation_allowed': box.rotation_allowed and request.global_rotation_allowed
        }
        for box in boxes
    ]

    # Expand quantities to individual items
    expanded_boxes = expand_boxes(boxes_dict)

    if not expanded_boxes:
        raise HTTPException(status_code=400, detail="No boxes to place")

    # Run 3D packing algorithm
    max_layers = request.stacking.max_layers if request.stacking.enabled else 1
    placed, remaining, layer_info = pack_3d_with_layers(
        trailer.length,
        trailer.width,
        trailer.height,
        expanded_boxes,
        max_layers=max_layers,
        stacking_enabled=request.stacking.enabled
    )

    # Validate solution
    if not validate_no_overlap(placed):
        raise HTTPException(status_code=500, detail="Internal error: overlapping placements")

    if not validate_within_bounds(placed, trailer.length, trailer.width, trailer.height):
        raise HTTPException(status_code=500, detail="Internal error: placements out of bounds")

    # Build response
    trailer_volume = trailer.length * trailer.width * trailer.height
    used_volume = sum(p.l * p.w * p.h for p in placed)
    fill_rate = used_volume / trailer_volume if trailer_volume > 0 else 0

    # Group placements by layer
    layers_dict: Dict[int, List[PlacedBox]] = defaultdict(list)
    for p in placed:
        layers_dict[p.layer].append(p)

    # Build layers response
    layers = []
    for layer_idx, z_base, layer_height in layer_info:
        placements = [
            Placement(
                sku=p.sku,
                x=round(p.x, 2),
                y=round(p.y, 2),
                z=round(p.z, 2),
                l=round(p.l, 2),
                w=round(p.w, 2),
                h=round(p.h, 2),
                rotated=p.rotated
            )
            for p in layers_dict[layer_idx]
        ]
        layers.append(Layer(
            layer_index=layer_idx,
            z_base=round(z_base, 2),
            layer_height=round(layer_height, 2),
            placements=placements
        ))

    # Count unplaced by SKU
    unplaced_count: Dict[str, int] = defaultdict(int)
    for box in remaining:
        unplaced_count[box.sku] += 1

    unplaced = [
        UnplacedItem(sku=sku, qty=qty)
        for sku, qty in sorted(unplaced_count.items())
    ]

    fits = len(remaining) == 0

    stats = Stats(
        trailer_volume=round(trailer_volume, 2),
        used_volume=round(used_volume, 2),
        fill_rate=round(fill_rate, 4),
        total_boxes_placed=len(placed),
        layers_used=len(layer_info)
    )

    return OptimizeResponse(
        fits=fits,
        stats=stats,
        layers=layers,
        unplaced=unplaced
    )


# Demo scenarios
DEMO_SCENARIOS = {
    "small": {
        "name": "Petit chargement",
        "trailer": {"length": 200, "width": 150, "height": 150, "unit": "cm"},
        "boxes": [
            {"sku": "BOX-A", "length": 40, "width": 30, "height": 30, "quantity": 5, "rotation_allowed": True},
            {"sku": "BOX-B", "length": 50, "width": 40, "height": 25, "quantity": 3, "rotation_allowed": True}
        ],
        "stacking": {"enabled": True, "max_layers": 3},
        "global_rotation_allowed": True
    },
    "medium": {
        "name": "Chargement moyen",
        "trailer": {"length": 600, "width": 240, "height": 250, "unit": "cm"},
        "boxes": [
            {"sku": "PALLET-A", "length": 120, "width": 80, "height": 100, "quantity": 8, "rotation_allowed": True},
            {"sku": "PALLET-B", "length": 100, "width": 100, "height": 80, "quantity": 6, "rotation_allowed": True},
            {"sku": "CRATE-S", "length": 60, "width": 40, "height": 50, "quantity": 10, "rotation_allowed": True}
        ],
        "stacking": {"enabled": True, "max_layers": 2},
        "global_rotation_allowed": True
    },
    "impossible": {
        "name": "Chargement impossible",
        "trailer": {"length": 300, "width": 200, "height": 200, "unit": "cm"},
        "boxes": [
            {"sku": "LARGE-1", "length": 100, "width": 80, "height": 100, "quantity": 10, "rotation_allowed": True},
            {"sku": "LARGE-2", "length": 90, "width": 70, "height": 90, "quantity": 8, "rotation_allowed": True},
            {"sku": "MEDIUM", "length": 60, "width": 50, "height": 60, "quantity": 15, "rotation_allowed": True}
        ],
        "stacking": {"enabled": True, "max_layers": 3},
        "global_rotation_allowed": True
    }
}


@app.get("/demos")
async def get_demos() -> Dict:
    """Get available demo scenarios."""
    return DEMO_SCENARIOS


@app.get("/demos/{scenario_id}")
async def get_demo(scenario_id: str) -> Dict:
    """Get a specific demo scenario."""
    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Demo '{scenario_id}' not found")
    return DEMO_SCENARIOS[scenario_id]
