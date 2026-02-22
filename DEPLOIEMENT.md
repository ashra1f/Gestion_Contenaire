# Guide de Deploiement

## Option 1: Railway (Recommande - Le plus simple)

Railway offre un hebergement gratuit avec 5$/mois de credits.

### Etape 1: Deployer le Backend

1. Creer un compte sur https://railway.app
2. Cliquer sur "New Project" > "Deploy from GitHub repo"
3. Connecter votre repo GitHub
4. Selectionner le dossier `backend`
5. Railway detecte automatiquement Python
6. Le deploiement demarre automatiquement
7. Une fois deploye, cliquer sur le service > Settings > Generate Domain
8. Copier l'URL (ex: `https://chourouk-backend.up.railway.app`)

### Etape 2: Deployer le Frontend

1. Dans le meme projet Railway, cliquer "New" > "GitHub Repo"
2. Selectionner le dossier `frontend`
3. Ajouter une variable d'environnement:
   - `VITE_API_URL` = `https://votre-backend.up.railway.app`
4. Generer un domaine pour le frontend

---

## Option 2: Render (Gratuit)

### Backend sur Render

1. Aller sur https://render.com
2. "New" > "Web Service"
3. Connecter GitHub et selectionner le repo
4. Configuration:
   - Name: `chourouk-api`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Cliquer "Create Web Service"
6. Noter l'URL du service

### Frontend sur Render

1. "New" > "Static Site"
2. Configuration:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
3. Ajouter variable: `VITE_API_URL` = URL du backend
4. Deployer

---

## Option 3: Vercel (Frontend) + Railway (Backend)

### Backend sur Railway
(Voir Option 1, Etape 1)

### Frontend sur Vercel

1. Aller sur https://vercel.com
2. "Import Project" depuis GitHub
3. Selectionner le dossier `frontend`
4. Ajouter variable d'environnement:
   - `VITE_API_URL` = `https://votre-backend.up.railway.app`
5. Deployer

---

## Option 4: VPS (OVH, Contabo, DigitalOcean)

Pour un controle total, deployer sur un VPS.

### Prerequis
- Ubuntu 22.04
- Docker installe

### Deploiement avec Docker Compose

Creer `docker-compose.yml` a la racine:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    restart: always

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: http://votre-domaine.com:8000
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always
```

Creer `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

Creer `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Lancer:
```bash
docker-compose up -d --build
```

---

## Option 5: Heroku

### Backend
```bash
cd backend
heroku create chourouk-api
git push heroku main
```

### Frontend
Utiliser Vercel ou Netlify (voir Option 3)

---

## Configuration CORS

Si vous avez des erreurs CORS, modifiez `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://votre-frontend.vercel.app",
        "https://votre-frontend.railway.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Resume des couts

| Hebergeur | Backend | Frontend | Cout/mois |
|-----------|---------|----------|-----------|
| Railway | Gratuit (5$ credits) | Gratuit | 0$ |
| Render | Gratuit (spin down) | Gratuit | 0$ |
| Vercel + Railway | Railway 5$ | Gratuit | 0-5$ |
| DigitalOcean | Droplet 6$ | Inclus | 6$ |
| Heroku | 7$ | Vercel gratuit | 7$ |

---

## Commandes utiles

### Pousser le code sur GitHub
```bash
cd chourouk
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/votre-user/chourouk.git
git push -u origin main
```

### Tester le backend en production
```bash
curl https://votre-backend.railway.app/health
```
