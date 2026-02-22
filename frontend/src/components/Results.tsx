import { OptimizeResponse } from '../types';

interface Props {
  result: OptimizeResponse;
}

export function Results({ result }: Props) {
  const { fits, stats, unplaced } = result;

  return (
    <div className="results-panel">
      <div className={`result-status ${fits ? 'success' : 'warning'}`}>
        <span className="status-icon">{fits ? '✓' : '!'}</span>
        <span className="status-text">
          {fits ? 'Tout rentre dans la remorque' : 'Certains colis ne rentrent pas'}
        </span>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{(stats.fill_rate * 100).toFixed(1)}%</div>
          <div className="stat-label">Taux de remplissage</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.total_boxes_placed}</div>
          <div className="stat-label">Colis placés</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.layers_used}</div>
          <div className="stat-label">Couches utilisées</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {(stats.used_volume / 1000000).toFixed(2)} m³
          </div>
          <div className="stat-label">Volume utilisé</div>
        </div>
      </div>

      <div className="volume-info">
        <div className="volume-bar">
          <div
            className="volume-fill"
            style={{ width: `${stats.fill_rate * 100}%` }}
          />
        </div>
        <div className="volume-text">
          {(stats.used_volume / 1000000).toFixed(3)} m³ /{' '}
          {(stats.trailer_volume / 1000000).toFixed(3)} m³
        </div>
      </div>

      {unplaced.length > 0 && (
        <div className="unplaced-section">
          <h4>Colis non placés</h4>
          <ul className="unplaced-list">
            {unplaced.map((item, index) => (
              <li key={index}>
                <span className="sku">{item.sku}</span>
                <span className="qty">x {item.qty}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
