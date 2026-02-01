# Application Web BingX Trading Bot

Application web pour trader et monitorer vos positions sur BingX (Perpetual et Standard Futures).

## 🎯 Fonctionnalités

### Backend (FastAPI)
- ✅ Configuration sécurisée des clés API
- ✅ Récupération balances Perpetual & Standard
- ✅ Récupération positions en temps réel
- ✅ Support retry automatique
- ✅ CORS activé pour frontend

### Frontend (HTML/CSS/JavaScript)
- ✅ Interface moderne et responsive
- ✅ Configuration API avec validation
- ✅ Affichage équilibrage & positions
- ✅ Rafraîchissement automatique (5s)
- ✅ Indicateur de connexion en temps réel
- ✅ Mobile-friendly

## 🚀 Installation & Lancement

### 1. Installer les dépendances

```bash
pip install fastapi uvicorn requests
```

### 2. Lancer le serveur

```bash
python app.py
```

Le serveur démarre sur `http://localhost:8000`

### 3. Accéder à l'application

Ouvrez dans votre navigateur : **http://localhost:8000**

## 🔐 Sécurité

- ✅ Clés API stockées en mémoire (lors de la session)
- ✅ Jamais sauvegardées sur le disque
- ✅ Communication HTTPS recommandée
- ✅ CORS activé pour accès local

⚠️ **Important** : Les clés API ne sont pas chiffrées. Utilisez uniquement en développement local.

## 📊 Endpoints API

### Configuration
- `POST /api/config` - Configure les clés API
- `GET /api/status` - Vérifie la connexion

### Balance
- `GET /api/balance/perpetual` - Balance Perpetual Futures
- `GET /api/balance/standard` - Balance Standard Futures

### Positions
- `GET /api/positions/perpetual` - Positions Perpetual
- `GET /api/positions/standard` - Positions Standard

### Santé
- `GET /api/health` - Santé de l'API

## 📱 Interface Web

### Zones principales
1. **Configuration API** - Entrée des clés BingX
2. **Perpetual Futures** - Balance et positions SWAP V2
3. **Standard Futures** - Balance et positions Contract V1
4. **Autorefresh** - Mise à jour auto toutes les 5 secondes

## 🔧 Architecture

```
app.py              (Backend FastAPI)
├── Configuration API
├── Balance endpoints
├── Positions endpoints
└── Serve frontend

static/
├── index.html       (Frontend HTML/CSS/JS)
├── Configuration UI
├── Dashboard UI
└── API client JS
```

## 🛠️ Développement Futur

- [ ] Trading en temps réel (ouverture/fermeture)
- [ ] Graphiques candlestick
- [ ] Historique des ordres
- [ ] Notifications WebSocket
- [ ] Base de données (SQLite/PostgreSQL)
- [ ] Authentification utilisateur
- [ ] Déploiement production (Docker)

## ⚠️ Limitations Actuelles

- Pas d'ouverture/fermeture de positions (à implémenter)
- Clés API en mémoire (pas persistent)
- Pas de chiffrement clés API
- Pas d'historique persistant

## 📚 Documentation BingX

- [API BingX Documentation](https://bingx-api.github.io/docs)
- Endpoints utilisés :
  - `/openApi/swap/v2/user/balance` - Perpetual balance
  - `/openApi/swap/v2/user/positions` - Perpetual positions
  - `/openApi/contract/v1/balance` - Standard balance
  - `/openApi/contract/v1/allPosition` - Standard positions

## 🐛 Dépannage

### "Erreur de connexion"
- Vérifiez que vos clés API sont correctes
- Vérifiez votre connexion Internet
- Attendez quelques secondes

### "Erreur d'authentification"
- Les clés API peuvent avoir des permissions limitées
- Générez de nouvelles clés avec accès lecture sur BingX

### Port 8000 déjà utilisé
```bash
python app.py --port 8001
```

---

**Créé** : 01/02/2026  
**Version** : 3.0.0
