import { OptimizeRequest, OptimizeResponse, DemoScenario } from './types';

// En développement, le proxy Vite redirige /api vers localhost:8000
// En production, on utilise directement l'URL du backend Render
const API_BASE = import.meta.env.VITE_API_URL || (
  import.meta.env.DEV ? '/api' : 'https://gestion-contenaire.onrender.com'
);

export async function optimizeLoading(request: OptimizeRequest): Promise<OptimizeResponse> {
  const response = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let message = 'Erreur lors de l\'optimisation';
    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      // Backend ne retourne pas du JSON valide
    }
    throw new Error(message);
  }

  return response.json();
}

export async function getDemos(): Promise<Record<string, DemoScenario>> {
  const response = await fetch(`${API_BASE}/demos`);
  if (!response.ok) {
    throw new Error('Erreur lors du chargement des démos');
  }
  return response.json();
}

export async function getDemo(id: string): Promise<DemoScenario> {
  const response = await fetch(`${API_BASE}/demos/${id}`);
  if (!response.ok) {
    throw new Error('Démo non trouvée');
  }
  return response.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
