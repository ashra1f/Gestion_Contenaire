"""Pydantic models for API validation and response."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Unit(str, Enum):
    CM = "cm"
    M = "m"


class Trailer(BaseModel):
    """Trailer dimensions."""
    length: float = Field(..., gt=0, description="Trailer length")
    width: float = Field(..., gt=0, description="Trailer width")
    height: float = Field(..., gt=0, description="Trailer height")
    unit: Unit = Field(default=Unit.CM, description="Unit of measurement")

    def to_cm(self) -> "Trailer":
        """Convert dimensions to centimeters."""
        if self.unit == Unit.M:
            return Trailer(
                length=self.length * 100,
                width=self.width * 100,
                height=self.height * 100,
                unit=Unit.CM
            )
        return self


class Box(BaseModel):
    """Box/package definition."""
    sku: str = Field(..., min_length=1, description="SKU/ID of the box")
    length: float = Field(..., gt=0, description="Box length")
    width: float = Field(..., gt=0, description="Box width")
    height: float = Field(..., gt=0, description="Box height")
    quantity: int = Field(..., ge=1, description="Number of boxes of this type")
    rotation_allowed: bool = Field(default=True, description="Allow 90° rotation")

    def to_cm(self, unit: Unit) -> "Box":
        """Convert dimensions to centimeters."""
        if unit == Unit.M:
            return Box(
                sku=self.sku,
                length=self.length * 100,
                width=self.width * 100,
                height=self.height * 100,
                quantity=self.quantity,
                rotation_allowed=self.rotation_allowed
            )
        return self

    def volume(self) -> float:
        """Calculate box volume."""
        return self.length * self.width * self.height


class StackingOptions(BaseModel):
    """Stacking configuration."""
    enabled: bool = Field(default=True, description="Enable stacking")
    max_layers: int = Field(default=3, ge=1, le=3, description="Maximum layers (1-3)")


class OptimizeRequest(BaseModel):
    """Request body for optimization endpoint."""
    trailer: Trailer
    boxes: List[Box]
    stacking: StackingOptions = Field(default_factory=StackingOptions)
    global_rotation_allowed: bool = Field(default=True, description="Global rotation setting")

    @field_validator('boxes')
    @classmethod
    def validate_boxes_not_empty(cls, v):
        if not v:
            raise ValueError('At least one box type is required')
        return v


class Placement(BaseModel):
    """Single box placement in the solution."""
    sku: str
    x: float
    y: float
    z: float
    l: float  # length after potential rotation
    w: float  # width after potential rotation
    h: float
    rotated: bool


class Layer(BaseModel):
    """A layer of placements."""
    layer_index: int
    z_base: float
    layer_height: float
    placements: List[Placement]


class UnplacedItem(BaseModel):
    """Unplaced box information."""
    sku: str
    qty: int


class Stats(BaseModel):
    """Solution statistics."""
    trailer_volume: float
    used_volume: float
    fill_rate: float
    total_boxes_placed: int
    layers_used: int


class OptimizeResponse(BaseModel):
    """Response from optimization endpoint."""
    fits: bool
    stats: Stats
    layers: List[Layer]
    unplaced: List[UnplacedItem]
