// API Types

export type Unit = 'cm' | 'm';

export interface Trailer {
  length: number;
  width: number;
  height: number;
  unit: Unit;
}

export interface Box {
  sku: string;
  length: number;
  width: number;
  height: number;
  quantity: number;
  rotation_allowed: boolean;
}

export interface StackingOptions {
  enabled: boolean;
  max_layers: number;
}

export interface OptimizeRequest {
  trailer: Trailer;
  boxes: Box[];
  stacking: StackingOptions;
  global_rotation_allowed: boolean;
}

export interface Placement {
  sku: string;
  x: number;
  y: number;
  z: number;
  l: number;
  w: number;
  h: number;
  rotated: boolean;
}

export interface Layer {
  layer_index: number;
  z_base: number;
  layer_height: number;
  placements: Placement[];
}

export interface UnplacedItem {
  sku: string;
  qty: number;
}

export interface Stats {
  trailer_volume: number;
  used_volume: number;
  fill_rate: number;
  total_boxes_placed: number;
  layers_used: number;
}

export interface OptimizeResponse {
  fits: boolean;
  stats: Stats;
  layers: Layer[];
  unplaced: UnplacedItem[];
}

export interface DemoScenario {
  name: string;
  trailer: Trailer;
  boxes: Box[];
  stacking: StackingOptions;
  global_rotation_allowed: boolean;
}

// Color palette for boxes
export const BOX_COLORS: string[] = [
  '#3498db', // Blue
  '#e74c3c', // Red
  '#2ecc71', // Green
  '#f39c12', // Orange
  '#9b59b6', // Purple
  '#1abc9c', // Teal
  '#e67e22', // Dark Orange
  '#34495e', // Dark Gray
  '#16a085', // Dark Teal
  '#c0392b', // Dark Red
];

export function getBoxColor(sku: string, allSkus: string[]): string {
  const index = allSkus.indexOf(sku);
  return BOX_COLORS[index % BOX_COLORS.length];
}
