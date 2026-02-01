# Changelog - BingX Trading Bot

Historique des versions et améliorations du bot de monitoring.

---

## [v3.0.0] - 2026-02-01

### 🎉 Nouveau
- ✅ **Complète refonte** : Bot de monitoring des positions
- ✅ **Perpetual Futures (Swap V2)** : Support complet
- ✅ **Standard Futures (Contract V1)** : Support complet
- ✅ **Endpoints optimisés** : Bons endpoints pour chaque type
- ✅ **Identification LONG/SHORT correcte** : Via positionSide
- ✅ **Rapport consolidé** : Résumé balances et P&L totaux
- ✅ **Historique ordres** : Standard Futures avec dates formatées
- ✅ **Type hints** : Code plus robuste

### 🔧 Améliorations
- ⚡ Retry automatique (3 tentatives, timeout 10s)
- 🎨 Formatage nombres avec séparateurs de milliers
- 📊 Affichage structuré avec emojis
- 🔄 Appels API centralisés (safe_api_call)
- 📈 Support levier et marge
- ⏱️ Temps d'exécution affiché
- 🎯 Détection fiable LONG/SHORT

### 🐛 Corrections
- Endpoint Standard Futures : v2 → v1 (/contract/v1/)
- Balance Standard : Gestion réponses en liste
- LONG/SHORT : Via positionSide au lieu de positionAmt

### 📚 Documentation
- README.md : Simplifié et actualisé
- Suppression fichiers obsolètes (6 fichiers)
- Nettoyage : Seuls 2 fichiers MD restants

---

## [v2.0.0] - 2026-01-28
- Archivé : Ancien bot ROI (XRP-USDT)

## [v1.0.0] - 2026-01-27
- Archivé : Version initiale
