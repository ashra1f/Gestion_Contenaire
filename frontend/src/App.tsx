import { useState, useEffect } from 'react';
import { TrailerForm } from './components/TrailerForm';
import { BoxesForm } from './components/BoxesForm';
import { OptionsForm } from './components/OptionsForm';
import { Results } from './components/Results';
import { View2D } from './components/View2D';
import { View3D } from './components/View3D';
import { optimizeLoading, getDemos } from './api';
import {
  Trailer,
  Box,
  StackingOptions,
  OptimizeResponse,
  DemoScenario,
} from './types';
import './App.css';

type ViewTab = 'results' | '2d' | '3d';

function App() {
  // Form state
  const [trailer, setTrailer] = useState<Trailer>({
    length: 600,
    width: 240,
    height: 250,
    unit: 'cm',
  });
  const [boxes, setBoxes] = useState<Box[]>([
    { sku: 'BOX-A', length: 80, width: 60, height: 50, quantity: 5, rotation_allowed: true },
    { sku: 'BOX-B', length: 60, width: 40, height: 40, quantity: 8, rotation_allowed: true },
  ]);
  const [stacking, setStacking] = useState<StackingOptions>({
    enabled: true,
    max_layers: 3,
  });
  const [globalRotation, setGlobalRotation] = useState(true);

  // Result state
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // View state
  const [activeTab, setActiveTab] = useState<ViewTab>('results');

  // Demo scenarios
  const [demos, setDemos] = useState<Record<string, DemoScenario>>({});

  useEffect(() => {
    getDemos().then(setDemos).catch(console.error);
  }, []);

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await optimizeLoading({
        trailer,
        boxes,
        stacking,
        global_rotation_allowed: globalRotation,
      });
      setResult(response);
      setActiveTab('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  const loadDemo = (demoId: string) => {
    const demo = demos[demoId];
    if (demo) {
      setTrailer(demo.trailer);
      setBoxes(demo.boxes);
      setStacking(demo.stacking);
      setGlobalRotation(demo.global_rotation_allowed);
      setResult(null);
      setError(null);
    }
  };

  const isValid = trailer.length > 0 && trailer.width > 0 && trailer.height > 0 && boxes.length > 0;

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-brand">
            <svg className="header-logo" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop offset="0%" stopColor="#F97316" />
                  <stop offset="100%" stopColor="#F59E0B" />
                </linearGradient>
              </defs>
              <rect x="3" y="15" width="42" height="22" rx="4" fill="url(#logoGrad)" />
              <rect x="8" y="20" width="12" height="12" rx="2" fill="white" opacity="0.9" />
              <rect x="24" y="20" width="12" height="12" rx="2" fill="white" opacity="0.7" />
              <circle cx="13" cy="40" r="3.5" fill="#334155" />
              <circle cx="35" cy="40" r="3.5" fill="#334155" />
              <path d="M6 15 L12 6 H36 L42 15" stroke="#F97316" strokeWidth="2.5" strokeLinecap="round" fill="none" />
              <path d="M18 3 L18 8 M24 1 L24 8 M30 3 L30 8" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" opacity="0.6" />
            </svg>
            <div className="header-text">
              <h1>Chourouk</h1>
              <p>Optimiseur de chargement intelligent</p>
            </div>
          </div>
        </div>
      </header>

      <div className="main-container">
        <aside className="sidebar">
          <div className="demo-section">
            <h4>Scenarios de demo</h4>
            <div className="demo-buttons">
              {Object.entries(demos).map(([id, demo]) => (
                <button
                  key={id}
                  className="btn btn-outline btn-sm"
                  onClick={() => loadDemo(id)}
                >
                  {demo.name}
                </button>
              ))}
            </div>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleOptimize();
            }}
          >
            <TrailerForm trailer={trailer} onChange={setTrailer} />
            <BoxesForm boxes={boxes} unit={trailer.unit} onChange={setBoxes} />
            <OptionsForm
              stacking={stacking}
              globalRotation={globalRotation}
              onStackingChange={setStacking}
              onGlobalRotationChange={setGlobalRotation}
            />

            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={!isValid || loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Optimisation en cours...
                  </>
                ) : (
                  'Optimiser le chargement'
                )}
              </button>
            </div>
          </form>

          {error && <div className="error-message">{error}</div>}
        </aside>

        <main className="content">
          {result ? (
            <>
              <div className="view-tabs">
                <button
                  className={`view-tab ${activeTab === 'results' ? 'active' : ''}`}
                  onClick={() => setActiveTab('results')}
                >
                  Resultats
                </button>
                <button
                  className={`view-tab ${activeTab === '2d' ? 'active' : ''}`}
                  onClick={() => setActiveTab('2d')}
                >
                  Vue 2D
                </button>
                <button
                  className={`view-tab ${activeTab === '3d' ? 'active' : ''}`}
                  onClick={() => setActiveTab('3d')}
                >
                  Vue 3D
                </button>
              </div>

              <div className="view-content">
                {activeTab === 'results' && <Results result={result} />}
                {activeTab === '2d' && <View2D result={result} trailer={trailer} />}
                {activeTab === '3d' && <View3D result={result} trailer={trailer} />}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">
                <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" width="80" height="80">
                  <rect x="10" y="25" width="60" height="40" rx="6" fill="#1E293B" opacity="0.15" />
                  <rect x="18" y="32" width="18" height="18" rx="3" fill="#F97316" opacity="0.3" />
                  <rect x="42" y="32" width="18" height="18" rx="3" fill="#F59E0B" opacity="0.3" />
                  <path d="M15 25 L24 12 H56 L65 25" stroke="#F97316" strokeWidth="2" strokeLinecap="round" opacity="0.3" />
                </svg>
              </div>
              <h2>Aucun resultat</h2>
              <p>
                Configurez votre remorque et vos colis, puis cliquez sur "Optimiser le
                chargement" pour voir le plan de placement.
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
