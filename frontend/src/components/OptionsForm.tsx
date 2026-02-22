import { StackingOptions } from '../types';

interface Props {
  stacking: StackingOptions;
  globalRotation: boolean;
  onStackingChange: (stacking: StackingOptions) => void;
  onGlobalRotationChange: (value: boolean) => void;
}

export function OptionsForm({
  stacking,
  globalRotation,
  onStackingChange,
  onGlobalRotationChange,
}: Props) {
  return (
    <div className="form-section">
      <h3>Options</h3>
      <div className="form-row options-row">
        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={stacking.enabled}
              onChange={(e) =>
                onStackingChange({ ...stacking, enabled: e.target.checked })
              }
            />
            Empilage activé
          </label>
        </div>

        {stacking.enabled && (
          <div className="form-group">
            <label>Couches max</label>
            <select
              value={stacking.max_layers}
              onChange={(e) =>
                onStackingChange({
                  ...stacking,
                  max_layers: parseInt(e.target.value),
                })
              }
            >
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
            </select>
          </div>
        )}

        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={globalRotation}
              onChange={(e) => onGlobalRotationChange(e.target.checked)}
            />
            Rotation 90° autorisée (global)
          </label>
        </div>
      </div>
    </div>
  );
}
