import React, { useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Html } from '@react-three/drei';
import * as THREE from 'three';
import { OptimizeResponse, Trailer, Placement, getBoxColor } from '../types';

interface Props {
  result: OptimizeResponse;
  trailer: Trailer;
}

interface BoxMeshProps {
  placement: Placement;
  color: string;
  scale: number;
  onClick: () => void;
  isSelected: boolean;
}

function BoxMesh({ placement, color, scale, onClick, isSelected }: BoxMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Scale dimensions (convert cm to scene units)
  const l = placement.l * scale;
  const w = placement.w * scale;
  const h = placement.h * scale;
  const x = placement.x * scale + l / 2;
  const y = placement.z * scale + h / 2; // Y is up in Three.js
  const z = placement.y * scale + w / 2;

  return (
    <mesh
      ref={meshRef}
      position={[x, y, z]}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={() => {
        setHovered(false);
        document.body.style.cursor = 'auto';
      }}
    >
      <boxGeometry args={[l, h, w]} />
      <meshStandardMaterial
        color={color}
        transparent
        opacity={hovered || isSelected ? 1 : 0.85}
      />
      {/* Edges */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(l, h, w)]} />
        <lineBasicMaterial color={isSelected ? '#ffffff' : '#000000'} linewidth={2} />
      </lineSegments>
    </mesh>
  );
}

interface TrailerMeshProps {
  trailer: Trailer;
  scale: number;
}

function TrailerMesh({ trailer, scale }: TrailerMeshProps) {
  // Convert to cm and scale
  const length = (trailer.unit === 'm' ? trailer.length * 100 : trailer.length) * scale;
  const width = (trailer.unit === 'm' ? trailer.width * 100 : trailer.width) * scale;
  const height = (trailer.unit === 'm' ? trailer.height * 100 : trailer.height) * scale;

  return (
    <group position={[length / 2, height / 2, width / 2]}>
      {/* Wireframe box */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(length, height, width)]} />
        <lineBasicMaterial color="#2c3e50" linewidth={2} />
      </lineSegments>
      {/* Semi-transparent floor */}
      <mesh position={[0, -height / 2 + 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[length, width]} />
        <meshStandardMaterial color="#ecf0f1" transparent opacity={0.5} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}

function Scene({
  result,
  trailer,
  selectedBox,
  setSelectedBox,
}: Props & {
  selectedBox: Placement | null;
  setSelectedBox: (p: Placement | null) => void;
}) {
  // Convert to cm for calculations
  const trailerCm = {
    length: trailer.unit === 'm' ? trailer.length * 100 : trailer.length,
    width: trailer.unit === 'm' ? trailer.width * 100 : trailer.width,
    height: trailer.unit === 'm' ? trailer.height * 100 : trailer.height,
  };

  // Scale factor to keep scene manageable (1 unit = 100cm)
  const scale = 0.01;

  // Get all unique SKUs for color mapping
  const allSkus = [...new Set(result.layers.flatMap((l) => l.placements.map((p) => p.sku)))];

  // Camera position based on trailer size
  const cameraDistance = Math.max(trailerCm.length, trailerCm.width, trailerCm.height) * scale * 2;

  return (
    <>
      <PerspectiveCamera
        makeDefault
        position={[cameraDistance, cameraDistance * 0.8, cameraDistance]}
        fov={50}
      />
      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        target={[
          (trailerCm.length * scale) / 2,
          (trailerCm.height * scale) / 2,
          (trailerCm.width * scale) / 2,
        ]}
      />

      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />
      <directionalLight position={[-10, 10, -5]} intensity={0.4} />

      {/* Trailer */}
      <TrailerMesh trailer={trailer} scale={scale} />

      {/* Boxes */}
      {result.layers.flatMap((layer) =>
        layer.placements.map((placement, index) => (
          <BoxMesh
            key={`${layer.layer_index}-${index}`}
            placement={placement}
            color={getBoxColor(placement.sku, allSkus)}
            scale={scale}
            onClick={() => setSelectedBox(placement)}
            isSelected={selectedBox === placement}
          />
        ))
      )}

      {/* Grid helper */}
      <gridHelper
        args={[10, 20, '#bdc3c7', '#ecf0f1']}
        position={[(trailerCm.length * scale) / 2, 0, (trailerCm.width * scale) / 2]}
      />
    </>
  );
}

export function View3D({ result, trailer }: Props) {
  const [selectedBox, setSelectedBox] = useState<Placement | null>(null);

  return (
    <div className="view-3d">
      <div className="canvas-container">
        <Canvas
          onClick={() => setSelectedBox(null)}
          gl={{ antialias: true }}
          dpr={[1, 2]}
        >
          <Scene
            result={result}
            trailer={trailer}
            selectedBox={selectedBox}
            setSelectedBox={setSelectedBox}
          />
        </Canvas>
      </div>

      {selectedBox && (
        <div className="info-panel">
          <h4>Colis sélectionné</h4>
          <table className="info-table">
            <tbody>
              <tr>
                <td>SKU</td>
                <td><strong>{selectedBox.sku}</strong></td>
              </tr>
              <tr>
                <td>Position</td>
                <td>X: {selectedBox.x}, Y: {selectedBox.y}, Z: {selectedBox.z} cm</td>
              </tr>
              <tr>
                <td>Dimensions</td>
                <td>{selectedBox.l} x {selectedBox.w} x {selectedBox.h} cm</td>
              </tr>
              <tr>
                <td>Volume</td>
                <td>{((selectedBox.l * selectedBox.w * selectedBox.h) / 1000000).toFixed(4)} m³</td>
              </tr>
              <tr>
                <td>Rotation</td>
                <td>{selectedBox.rotated ? 'Oui (90°)' : 'Non'}</td>
              </tr>
            </tbody>
          </table>
          <button className="btn btn-secondary btn-sm" onClick={() => setSelectedBox(null)}>
            Fermer
          </button>
        </div>
      )}

      <div className="controls-hint">
        <p>Clic gauche + glisser : Rotation | Molette : Zoom | Clic droit + glisser : Pan</p>
      </div>

      <div className="legend">
        <h5>Légende</h5>
        <div className="legend-items">
          {[...new Set(result.layers.flatMap((l) => l.placements.map((p) => p.sku)))].map(
            (sku) => (
              <div key={sku} className="legend-item">
                <span
                  className="color-box"
                  style={{
                    backgroundColor: getBoxColor(
                      sku,
                      [...new Set(result.layers.flatMap((l) => l.placements.map((p) => p.sku)))]
                    ),
                  }}
                />
                <span>{sku}</span>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
