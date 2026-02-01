# 📊 BingX Trading Bot - Monitoring Portefeuille

Bot Python pour surveiller et analyser vos positions de trading sur **BingX** (Perpetual Futures et Standard Futures).

## 🎯 Fonctionnalités

Le bot récupère et affiche en temps réel :

- ✅ **Perpetual Futures (Swap V2)**
  - Solde du compte et disponibilité
  - Positions LONG/SHORT avec P&L
  
- ✅ **Standard Futures (Contract V1)**
  - Solde du compte
  - Positions LONG/SHORT avec levier et marge
  - Historique des ordres

- ✅ **Résumé Consolidé**
  - Solde total
  - P&L global
  - Nombre total de positions

## 🚀 Installation

### Prérequis
- Python 3.8+
- Compte BingX avec API activée

### Dépendances
```bash
pip install requests
```

## ⚙️ Configuration

### Clés API BingX

**Option 1 : Variables d'environnement**
```bash
export BINGX_API_KEY="votre_cle_api"
export BINGX_API_SECRET="votre_secret_api"
```

**Option 2 : Fichier config.json**
```json
{
    "BINGX_API_KEY": "votre_cle_api",
    "BINGX_API_SECRET": "votre_secret_api"
}
```

## 🏃 Lancement

```bash
python trading_bot.py
```

Le bot affichera :
- 💰 Solde total et disponible
- 📊 Positions LONG/SHORT
- 📈 P&L par position
- ✅ Résumé consolidé

Pour arrêter : `Ctrl+C`

## ⚠️ Avertissements

- **Trading à risque** : Utilisez ce bot à vos propres risques
- **Testez d'abord** : Utilisez le mode simulation avant le trading réel
- **Capital** : N'investissez que ce que vous pouvez vous permettre de perdre
- **Surveillance** : Surveillez régulièrement les performances du bot

## 📝 License

MIT
