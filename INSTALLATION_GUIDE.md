# 🚀 Guide d'Installation - Application Web BingX Trading

Guide complet pour installer et lancer l'application web de trading BingX.

## 📋 Prérequis

- Python 3.8+
- Compte BingX avec API activée
- Navigateur web moderne (Chrome, Firefox, Safari, Edge)
- Connexion Internet

## ⚡ Installation Rapide (5 minutes)

### 1. Installer les dépendances

```bash
cd /workspaces/PersonalPythonBot
pip install -r requirements.txt
```

### 2. Lancer le serveur

```bash
python app.py
```

Vous verrez :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Ouvrir l'application

Dans votre navigateur, allez à : **http://localhost:8000**

## 🎯 Configuration

### Étape 1 : Obtenir vos clés API BingX

1. Allez sur [BingX.com](https://bingx.com)
2. Connectez-vous à votre compte
3. Allez dans **Paramètres → API**
4. Créez une nouvelle clé API
5. Copiez :
   - **Clé API** (API Key)
   - **Secret API** (API Secret)

### Étape 2 : Configurer dans l'app

1. Collez votre **Clé API** dans le premier champ
2. Collez votre **Secret API** dans le second champ
3. Cliquez sur **🔐 Connecter**

✅ Vous verrez "Connecté avec succès!" et le dashboard s'affichera.

## 📊 Utilisation

### Dashboard Perpetual Futures
- Affiche votre balance SWAP V2
- Liste vos positions LONG/SHORT
- Montre votre P&L en temps réel
- Bouton 🔄 pour rafraîchir

### Dashboard Standard Futures
- Affiche votre balance Contract V1
- Liste vos positions avec levier
- Montre votre P&L
- Bouton 🔄 pour rafraîchir

### Autorefresh
- Les données se mettent à jour automatiquement toutes les **5 secondes**
- L'heure de dernière mise à jour s'affiche en bas

## 🔐 Sécurité

### ✅ Ce qui est sécurisé
- Les clés API sont stockées **en mémoire uniquement**
- Elles ne sont **jamais sauvegardées** sur le disque
- Elles ne sont **jamais loggées**
- Communication via HTTPS recommandée en production

### ⚠️ Recommandations
- Utilisez des **clés API de lecture seule** si possible
- Ne partagez pas votre accès avec d'autres
- Regénérez les clés si vous les suspectez compromises
- Fermez l'application quand vous avez fini

## 🛑 Arrêter l'application

Appuyez sur `Ctrl+C` dans le terminal.

## 🔧 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le port 8000 est libre
lsof -i :8000

# Utiliser un autre port
python -c "import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8001)"
```

### "Erreur de connexion" au configurer
- Vérifiez que vos clés sont correctes
- Vérifiez votre connexion Internet
- Les clés API ont peut-être des permissions insuffisantes

### "Erreur Perpetual" ou "Erreur Standard Futures"
- Attendez quelques secondes
- Vérifiez que vous avez des positions ouvertes
- Essayez de cliquer sur le bouton 🔄

### Le page reste blanche
- Appuyez sur F5 pour rafraîchir
- Vérifiez la console (F12) pour les erreurs
- Vérifiez que `http://localhost:8000` est accessible

## 📝 Fichiers du Projet

```
/workspaces/PersonalPythonBot/
├── app.py                       (Backend FastAPI)
├── requirements.txt             (Dépendances Python)
├── static/
│   └── index.html              (Frontend web)
├── README.md                    (Documentation principale)
├── WEB_APP_README.md           (Cette documentation)
└── trading_bot.py              (Bot CLI original)
```

## 🎮 Fonctionnalités Disponibles

### ✅ Actuellement disponibles
- 📊 Monitoring balances en temps réel
- 📈 Affichage positions avec P&L
- 🔄 Rafraîchissement automatique
- 🔐 Configuration sécurisée des clés API
- 📱 Interface responsive (mobile-friendly)

### 🔜 À venir
- 📋 Ouverture/fermeture positions
- 📊 Graphiques candlestick
- 📜 Historique ordres
- 🔔 Notifications en temps réel
- 💾 Sauvegarde historique

## 📚 Ressources

- [API BingX Documentation](https://bingx-api.github.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

## 💡 Tips

- **Clés API** : Créez des clés avec permissions **Read-only** pour la sécurité
- **Monitoring** : L'app se met à jour automatiquement, pas besoin de rafraîchir manuellement
- **Mobile** : L'interface s'adapte à tous les écrans
- **Performances** : Le serveur utilise très peu de ressources (< 50 MB RAM)

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez la section "Dépannage"
2. Vérifiez les logs du serveur (console)
3. Vérifiez la console du navigateur (F12)
4. Consultez [BingX API Docs](https://bingx-api.github.io/docs)

---

**Besoin d'aide ?** Consultez le fichier [WEB_APP_README.md](WEB_APP_README.md) pour plus de détails.

**Version** : 3.0.0  
**Dernière mise à jour** : 01/02/2026
