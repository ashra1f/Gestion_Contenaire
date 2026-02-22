import React, { useState } from 'react';
import { OptimizeResponse, Trailer, Placement, getBoxColor } from '../types';

interface Props {
  result: OptimizeResponse;
  trailer: Trailer;
}

export function View2D({ result, trailer }: Props) {
  const [activeLayer, setActiveLayer] = useState(1);
  const [hoveredBox, setHoveredBox] = useState<Placement | null>(null);

  // Convert trailer to cm for display
  const trailerCm = {
    length: trailer.unit === 'm' ? trailer.length * 100 : trailer.length,
    width: trailer.unit === 'm' ? trailer.width * 100 : trailer.width,
  };

  // Scale for SVG
  const padding = 40;
  const maxWidth = 600;
  const maxHeight = 400;
  const scale = Math.min(
    (maxWidth - padding * 2) / trailerCm.length,
    (maxHeight - padding * 2) / trailerCm.width
  );

  const svgWidth = trailerCm.length * scale + padding * 2;
  const svgHeight = trailerCm.width * scale + padding * 2;

  // Get all unique SKUs for color mapping
  const allSkus = [...new Set(result.layers.flatMap((l) => l.placements.map((p) => p.sku)))];

  // Get current layer placements
  const currentLayer = result.layers.find((l) => l.layer_index === activeLayer);
  const placements = currentLayer?.placements || [];

  return (
    <div className="view-2d">
      <div className="layer-tabs">
        {[1, 2, 3].map((layer) => {
          const layerData = result.layers.find((l) => l.layer_index === layer);
          const hasBoxes = layerData && layerData.placements.length > 0;
          return (
            <button
              key={layer}
              className={`layer-tab ${activeLayer === layer ? 'active' : ''} ${
                !hasBoxes ? 'empty' : ''
              }`}
              onClick={() => setActiveLayer(layer)}
              disabled={!hasBoxes}
            >
              Couche {layer}
              {hasBoxes && <span className="box-count">({layerData!.placements.length})</span>}
            </button>
          );
        })}
      </div>

      <div className="svg-container">
        <svg width={svgWidth} height={svgHeight} viewBox={`0 0 ${svgWidth} ${svgHeight}`}>
          {/* Trailer outline */}
          <rect
            x={padding}
            y={padding}
            width={trailerCm.length * scale}
            height={trailerCm.width * scale}
            fill="#f8f9fa"
            stroke="#343a40"
            strokeWidth="2"
          />

          {/* Grid lines */}
          {Array.from({ length: Math.floor(trailerCm.length / 50) + 1 }).map((_, i) => (
            <line
              key={`v-${i}`}
              x1={padding + i * 50 * scale}
              y1={padding}
              x2={padding + i * 50 * scale}
              y2={padding + trailerCm.width * scale}
              stroke="#dee2e6"
              strokeWidth="0.5"
            />
          ))}
          {Array.from({ length: Math.floor(trailerCm.width / 50) + 1 }).map((_, i) => (
            <line
              key={`h-${i}`}
              x1={padding}
              y1={padding + i * 50 * scale}
              x2={padding + trailerCm.length * scale}
              y2={padding + i * 50 * scale}
              stroke="#dee2e6"
              strokeWidth="0.5"
            />
          ))}

          {/* Boxes */}
          {placements.map((placement, index) => {
            const color = getBoxColor(placement.sku, allSkus);
            const isHovered = hoveredBox === placement;
            return (
              <g key={index}>
                <rect
                  x={padding + placement.x * scale}
                  y={padding + placement.y * scale}
                  width={placement.l * scale}
                  height={placement.w * scale}
                  fill={color}
                  fillOpacity={isHovered ? 1 : 0.8}
                  stroke={isHovered ? '#000' : '#fff'}
                  strokeWidth={isHovered ? 2 : 1}
                  onMouseEnter={() => setHoveredBox(placement)}
                  onMouseLeave={() => setHoveredBox(null)}
                  style={{ cursor: 'pointer' }}
                />
                {/* SKU label if box is big enough */}
                {placement.l * scale > 30 && placement.w * scale > 20 && (
                  <text
                    x={padding + placement.x * scale + (placement.l * scale) / 2}
                    y={padding + placement.y * scale + (placement.w * scale) / 2}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="10"
                    fill="#fff"
                    fontWeight="bold"
                    pointerEvents="none"
                  >
                    {placement.sku}
                  </text>
                )}
              </g>
            );
          })}

          {/* Axis labels */}
          <text x={svgWidth / 2} y={svgHeight - 5} textAnchor="middle" fontSize="12">
            Longueur ({trailerCm.length} cm)
          </text>
          <text
            x={10}
            y={svgHeight / 2}
            textAnchor="middle"
            fontSize="12"
            transform={`rotate(-90, 10, ${svgHeight / 2})`}
          >
            Largeur ({trailerCm.width} cm)
          </text>
        </svg>
      </div>

      {hoveredBox && (
        <div className="tooltip-2d">
          <strong>{hoveredBox.sku}</strong>
          <br />
          Position: ({hoveredBox.x}, {hoveredBox.y})
          <br />
          Dimensions: {hoveredBox.l} x {hoveredBox.w} x {hoveredBox.h} cm
          <br />
          {hoveredBox.rotated && <span className="rotated-badge">Rotation 90°</span>}
        </div>
      )}

      {currentLayer && (
        <div className="layer-info">
          <p>
            <strong>Couche {activeLayer}</strong> - Z: {currentLayer.z_base} cm - Hauteur:{' '}
            {currentLayer.layer_height} cm
          </p>
        </div>
      )}
    </div>
  );
}
