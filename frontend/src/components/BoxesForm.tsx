import { Box, Unit } from '../types';

interface Props {
  boxes: Box[];
  unit: Unit;
  onChange: (boxes: Box[]) => void;
}

export function BoxesForm({ boxes, unit, onChange }: Props) {
  const addBox = () => {
    const newBox: Box = {
      sku: `BOX-${boxes.length + 1}`,
      length: 50,
      width: 40,
      height: 30,
      quantity: 1,
      rotation_allowed: true,
    };
    onChange([...boxes, newBox]);
  };

  const removeBox = (index: number) => {
    onChange(boxes.filter((_, i) => i !== index));
  };

  const updateBox = (index: number, field: keyof Box, value: string | number | boolean) => {
    const updated = boxes.map((box, i) => {
      if (i === index) {
        return { ...box, [field]: value };
      }
      return box;
    });
    onChange(updated);
  };

  return (
    <div className="form-section">
      <div className="section-header">
        <h3>Colis</h3>
        <button type="button" className="btn btn-secondary" onClick={addBox}>
          + Ajouter un colis
        </button>
      </div>

      {boxes.length === 0 ? (
        <p className="empty-message">Aucun colis ajouté. Cliquez sur "Ajouter un colis" pour commencer.</p>
      ) : (
        <table className="boxes-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>L ({unit})</th>
              <th>l ({unit})</th>
              <th>H ({unit})</th>
              <th>Qté</th>
              <th>Rotation</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {boxes.map((box, index) => (
              <tr key={index}>
                <td>
                  <input
                    type="text"
                    value={box.sku}
                    onChange={(e) => updateBox(index, 'sku', e.target.value)}
                    className="input-sku"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={box.length}
                    onChange={(e) => updateBox(index, 'length', parseFloat(e.target.value) || 0)}
                    className="input-dim"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={box.width}
                    onChange={(e) => updateBox(index, 'width', parseFloat(e.target.value) || 0)}
                    className="input-dim"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={box.height}
                    onChange={(e) => updateBox(index, 'height', parseFloat(e.target.value) || 0)}
                    className="input-dim"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={box.quantity}
                    onChange={(e) => updateBox(index, 'quantity', parseInt(e.target.value) || 1)}
                    className="input-qty"
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={box.rotation_allowed}
                    onChange={(e) => updateBox(index, 'rotation_allowed', e.target.checked)}
                  />
                </td>
                <td>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => removeBox(index)}
                  >
                    X
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
