# Optimiseur de Chargement de Remorque

Application web pour optimiser le chargement de colis dans une remorque avec visualisation 2D et 3D.

## Fonctionnalites

- **Calcul d'optimisation 3D** : Algorithme MaxRects pour le placement optimal des colis
- **Empilage configurable** : Jusqu'a 3 couches avec gestion de la hauteur
- **Rotation 90 degres** : Option de rotation par colis ou globale
- **Visualisation 2D** : Vue de dessus par couche (SVG interactif)
- **Visualisation 3D** : Scene Three.js avec controles orbit
- **Statistiques** : Taux de remplissage, volume utilise, colis places
- **Scenarios de demo** : 3 scenarios precharges (petit, moyen, impossible)

## Architecture

```
chourouk/
├── backend/           # API FastAPI (Python)
│   ├── app/
│   │   ├── main.py    # Endpoints API
│   │   ├── models.py  # Modeles Pydantic
│   │   └── packing.py # Algorithme de bin packing
│   └── tests/         # Tests unitaires
└── frontend/          # Application React (TypeScript)
    └── src/
        ├── components/  # Composants React
        ├── api.ts       # Client API
        └── types.ts     # Types TypeScript
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm ou yarn

### Backend

```bash
cd backend

# Creer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dependances
pip install -r requirements.txt

# Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

Le backend sera disponible sur http://localhost:8000

### Frontend

```bash
cd frontend

# Installer les dependances
npm install

# Lancer le serveur de developpement
npm run dev
```

Le frontend sera disponible sur http://localhost:3000

## Tests

### Tests Backend

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

### POST /optimize

Calcule le placement optimal des colis.

**Request:**
```json
{
  "trailer": {
    "length": 600,
    "width": 240,
    "height": 250,
    "unit": "cm"
  },
  "boxes": [
    {
      "sku": "BOX-A",
      "length": 80,
      "width": 60,
      "height": 50,
      "quantity": 5,
      "rotation_allowed": true
    }
  ],
  "stacking": {
    "enabled": true,
    "max_layers": 3
  },
  "global_rotation_allowed": true
}
```

**Response:**
```json
{
  "fits": true,
  "stats": {
    "trailer_volume": 36000000,
    "used_volume": 1200000,
    "fill_rate": 0.0333,
    "total_boxes_placed": 5,
    "layers_used": 1
  },
  "layers": [
    {
      "layer_index": 1,
      "z_base": 0,
      "layer_height": 50,
      "placements": [
        {
          "sku": "BOX-A",
          "x": 0,
          "y": 0,
          "z": 0,
          "l": 80,
          "w": 60,
          "h": 50,
          "rotated": false
        }
      ]
    }
  ],
  "unplaced": []
}
```

### GET /health

Verification de l'etat du service.

### GET /demos

Liste des scenarios de demonstration.

### GET /demos/{id}

Details d'un scenario specifique (small, medium, impossible).

## Algorithme

L'application utilise l'algorithme **MaxRects Best Short Side Fit** pour le bin packing 2D, etendu en 3D avec une approche couche par couche:

1. **Tri** : Les colis sont tries par volume decroissant
2. **Placement par couche** : Chaque couche est remplie avec MaxRects
3. **Gestion de la hauteur** : La hauteur d'une couche = max(hauteur des colis)
4. **Empilage** : Jusqu'a 3 couches superposees

### Contraintes respectees

- Pas de chevauchement entre les colis
- Colis dans les limites de la remorque
- Rotation 90 degres optionnelle (swap L et l)
- Hauteur totale <= hauteur remorque

## Scenarios de Demo

### Petit chargement
- Remorque: 200 x 150 x 150 cm
- 5 colis BOX-A (40x30x30) + 3 colis BOX-B (50x40x25)
- Resultat: Tout rentre

### Chargement moyen
- Remorque: 600 x 240 x 250 cm
- 8 palettes A + 6 palettes B + 10 caisses
- Resultat: Optimisation sur 2 couches

### Chargement impossible
- Remorque: 300 x 200 x 200 cm
- Trop de colis volumineux
- Resultat: Colis non places affiches

## Utilisation de l'interface

1. **Configurer la remorque** : Dimensions et unite (cm ou m)
2. **Ajouter les colis** : SKU, dimensions, quantite, option rotation
3. **Options** : Activer/desactiver empilage, nombre de couches max
4. **Optimiser** : Cliquer sur "Optimiser le chargement"
5. **Visualiser** :
   - Onglet Resultats: Statistiques et colis non places
   - Onglet 2D: Vue de dessus par couche
   - Onglet 3D: Vue interactive (rotation, zoom, clic sur colis)

## Technologies

- **Backend** : FastAPI, Pydantic, Python
- **Frontend** : React, TypeScript, Vite
- **3D** : Three.js, React Three Fiber, Drei
- **Tests** : Pytest
