import React from 'react';
import { Trailer, Unit } from '../types';

interface Props {
  trailer: Trailer;
  onChange: (trailer: Trailer) => void;
}

export function TrailerForm({ trailer, onChange }: Props) {
  const handleChange = (field: keyof Trailer, value: number | Unit) => {
    onChange({ ...trailer, [field]: value });
  };

  return (
    <div className="form-section">
      <h3>Remorque</h3>
      <div className="form-row">
        <div className="form-group">
          <label>Longueur</label>
          <input
            type="number"
            min="1"
            step="0.1"
            value={trailer.length}
            onChange={(e) => handleChange('length', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="form-group">
          <label>Largeur</label>
          <input
            type="number"
            min="1"
            step="0.1"
            value={trailer.width}
            onChange={(e) => handleChange('width', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="form-group">
          <label>Hauteur</label>
          <input
            type="number"
            min="1"
            step="0.1"
            value={trailer.height}
            onChange={(e) => handleChange('height', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="form-group">
          <label>Unité</label>
          <select
            value={trailer.unit}
            onChange={(e) => handleChange('unit', e.target.value as Unit)}
          >
            <option value="cm">Centimètres (cm)</option>
            <option value="m">Mètres (m)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
