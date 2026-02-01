import requests
import hmac
import hashlib
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# ==========================================
# CONFIGURATION
# ==========================================

BINGX_API_URL = "https://open-api.bingx.com"
REQUEST_TIMEOUT = 10  # secondes
MAX_RETRIES = 3

def load_api_keys():
    """Charge les clés API depuis config.json ou variables d'environnement"""
    api_key = None
    api_secret = None
    
    # Priorité 1: config.json
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
                api_key = config.get("BINGX_API_KEY")
                api_secret = config.get("BINGX_API_SECRET")
    except Exception as e:
        print(f"Erreur lors de la lecture de config.json: {e}")
    
    # Fallback: variables d'environnement
    if not api_key or not api_secret:
        api_key = api_key or os.getenv("BINGX_API_KEY")
        api_secret = api_secret or os.getenv("BINGX_API_SECRET")
    
    return api_key, api_secret

API_KEY, API_SECRET = load_api_keys()

# ==========================================
# FONCTIONS API PERPETUAL (SWAP V2)
# ==========================================

# ==========================================
# UTILITAIRES
# ==========================================

def sign_request(params: Dict, secret: str) -> str:
    """Signe une requête avec HMAC SHA256."""
    query = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return signature

def format_number(num: float, decimals: int = 2) -> str:
    """Formate un nombre avec séparateur des milliers."""
    try:
        return f"{float(num):,.{decimals}f}"
    except:
        return str(num)

def safe_api_call(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Effectue un appel API avec retry automatique."""
    if params is None:
        params = {}
    
    params["timestamp"] = str(int(time.time() * 1000))
    params["signature"] = sign_request(params, API_SECRET)
    
    headers = {"X-BX-APIKEY": API_KEY}
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                BINGX_API_URL + endpoint,
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            try:
                data = response.json()
            except:
                data = response.text
            return data
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"⏱️ Timeout, nouvelle tentative {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(1)
            else:
                print(f"❌ Erreur: Timeout après {MAX_RETRIES} tentatives")
                return None
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"⚠️ Erreur: {e}, nouvelle tentative {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(1)
            else:
                print(f"❌ Erreur: {e}")
                return None
    return None

def print_header(title: str) -> None:
    """Affiche un en-tête formaté."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def debug_position_fields(position: Dict) -> None:
    """Affiche tous les champs d'une position pour debug."""
    print("\n   🔍 Champs de la position:")
    for key, value in position.items():
        print(f"       {key}: {value}")

def get_swap_balance() -> Optional[Dict]:
    """
    Récupère le solde du compte Perpetual Futures (Swap V2).
    """
    endpoint = "/openApi/swap/v2/user/balance"
    data = safe_api_call(endpoint)
    
    if not data or not isinstance(data, dict):
        print(f"❌ Erreur: Réponse invalide")
        return None
    
    if data.get('code') != 0:
        print(f"❌ Erreur Solde Perpetual: {data.get('msg', data)}")
        return None
    
    balance_data = data.get('data', {}).get('balance', {})
    
    if not balance_data:
        print("⚠️ Aucun solde Perpetual trouvé.")
        return None
    
    balance = float(balance_data.get('balance', 0))
    available = float(balance_data.get('availableMargin', 0))
    pnl = float(balance_data.get('unrealizedProfit', 0))
    
    print("\n💼 --- BALANCE PERPETUAL FUTURES (SWAP V2) ---")
    print(f"🏦 Solde Total:       {format_number(balance, 4)} USDT")
    print(f"💵 Disponible:        {format_number(available, 4)} USDT")
    print(f"📊 P&L (Non-Réalisé): {format_number(pnl, 4)} USDT")
    
    return balance_data

def get_swap_positions() -> int:
    """
    Récupère les positions ouvertes sur Perpetual Futures (Swap V2).
    Retourne le nombre de positions ouvertes.
    """
    endpoint = "/openApi/swap/v2/user/positions"
    data = safe_api_call(endpoint)
    
    if not data or not isinstance(data, dict):
        print(f"❌ Erreur: Réponse invalide")
        return 0
    
    if data.get('code') != 0:
        print(f"❌ Erreur Positions Perpetual: {data.get('msg', data)}")
        return 0
    
    positions_list = data.get('data', [])
    open_positions = [p for p in positions_list if float(p.get('positionAmt', 0)) != 0]
    
    print("\n📈 --- POSITIONS OUVERTES (PERPETUAL FUTURES) ---")
    
    if not open_positions:
        print("   ✅ Aucune position ouverte")
        return 0
    
    total_pnl = 0
    for i, pos in enumerate(open_positions, 1):
        symbol = pos.get('symbol', 'N/A')
        amt = float(pos.get('positionAmt', 0))
        entry = float(pos.get('entryPrice', 0))
        pnl = float(pos.get('unrealizedProfit', 0))
        leverage = pos.get('leverage', 'N/A')
        margin = float(pos.get('margin', 0))
        
        # Détecter LONG/SHORT via le champ 'positionSide' ou fallback sur positionAmt
        pos_side = pos.get('positionSide', '').upper()
        if pos_side == 'LONG':
            side = "📈 LONG"
        elif pos_side == 'SHORT':
            side = "📉 SHORT"
        else:
            # Fallback: utiliser le signe de positionAmt
            side = "📈 LONG" if amt > 0 else "📉 SHORT"
        
        total_pnl += pnl
        
        print(f"\n   [{i}] {symbol} {side}")
        print(f"       Qté: {format_number(abs(amt), 6)} | Entrée: {format_number(entry, 2)}")
        print(f"       Levier: {leverage}x | Marge: {format_number(margin, 4)} USDT")
        print(f"       P&L: {format_number(pnl, 4)} USDT")
    
    print(f"\n   📊 P&L Total: {format_number(total_pnl, 4)} USDT")
    return len(open_positions)

# ==========================================
# FONCTIONS API STANDARD FUTURES
# ==========================================

def get_standard_futures_balance() -> Optional[Dict]:
    """
    Récupère le solde du compte Standard Futures (Contract V1).
    """
    endpoint = "/openApi/contract/v1/balance"
    data = safe_api_call(endpoint)
    
    if not data or not isinstance(data, dict):
        print(f"❌ Erreur: Réponse invalide")
        return None
    
    if data.get('code') != 0:
        print(f"❌ Erreur Solde Standard Futures: {data.get('msg', data)}")
        return None
    
    balance_list = data.get('data', [])
    
    if isinstance(balance_list, list) and len(balance_list) > 0:
        balance_data = balance_list[0]
    else:
        balance_data = balance_list if isinstance(balance_list, dict) else {}
    
    if not balance_data:
        print("⚠️ Aucun solde Standard Futures trouvé.")
        return None
    
    balance = float(balance_data.get('balance', 0))
    available = float(balance_data.get('available', 0))
    pnl = float(balance_data.get('unrealizedProfit', 0))
    
    print("\n💼 --- BALANCE STANDARD FUTURES (CONTRACT V1) ---")
    print(f"🏦 Solde Total:       {format_number(balance, 2)} USDT")
    print(f"💵 Disponible:        {format_number(available, 2)} USDT")
    print(f"📊 P&L (Non-Réalisé): {format_number(pnl, 2)} USDT")
    
    return balance_data

def get_standard_futures_positions() -> int:
    """
    Récupère les positions ouvertes sur Standard Futures (Contract V1).
    Retourne le nombre de positions ouvertes.
    """
    endpoint = "/openApi/contract/v1/allPosition"
    data = safe_api_call(endpoint)
    
    if not data or not isinstance(data, dict):
        print(f"❌ Erreur: Réponse invalide")
        return 0
    
    if data.get('code') != 0:
        print(f"❌ Erreur Positions Standard Futures: {data.get('msg', data)}")
        return 0
    
    positions_list = data.get('data', [])
    open_positions = [p for p in positions_list if float(p.get('positionAmt', 0)) != 0]
    
    print("\n📈 --- POSITIONS OUVERTES (STANDARD FUTURES) ---")
    
    if not open_positions:
        print("   ✅ Aucune position ouverte")
        return 0
    
    total_pnl = 0
    for i, pos in enumerate(open_positions, 1):
        symbol = pos.get('symbol', 'N/A')
        amt = float(pos.get('positionAmt', 0))
        entry = float(pos.get('entryPrice', 0))
        pnl = float(pos.get('unrealizedProfit', 0))
        margin = float(pos.get('margin', 0))
        leverage = pos.get('leverage', 'N/A')
        
        # Détecter LONG/SHORT via le champ 'positionSide'
        pos_side = pos.get('positionSide', '').upper()
        if pos_side == 'LONG':
            side = "📈 LONG"
        elif pos_side == 'SHORT':
            side = "📉 SHORT"
        else:
            # Fallback: utiliser le signe de positionAmt
            side = "📈 LONG" if amt > 0 else "📉 SHORT"
        
        total_pnl += pnl
        
        print(f"\n   [{i}] {symbol} {side}")
        print(f"       Qté: {format_number(abs(amt), 8)} | Entrée: {format_number(entry, 2)}")
        print(f"       Levier: {leverage}x | Marge: {format_number(margin, 4)} USDT")
        print(f"       P&L: {format_number(pnl, 4)} USDT")
    
    print(f"\n   📊 P&L Total: {format_number(total_pnl, 4)} USDT | 📍 Positions: {len(open_positions)}")
    return len(open_positions)

def get_standard_futures_orders(limit: int = 10) -> int:
    """
    Récupère l'historique des ordres sur Standard Futures (Contract V1).
    Retourne le nombre d'ordres affichés.
    """
    endpoint = "/openApi/contract/v1/allOrders"
    data = safe_api_call(endpoint)
    
    if not data or not isinstance(data, dict):
        print(f"❌ Erreur: Réponse invalide")
        return 0
    
    if data.get('code') != 0:
        print(f"❌ Erreur Historique Standard Futures: {data.get('msg', data)}")
        return 0
    
    orders_list = data.get('data', [])
    
    print(f"\n📋 --- HISTORIQUE DES ORDRES (DERNIER {limit}) ---")
    
    if not orders_list:
        print("   ✅ Aucun ordre trouvé")
        return 0
    
    # Afficher les N derniers ordres
    displayed_orders = orders_list[-limit:]
    for i, order in enumerate(displayed_orders, 1):
        symbol = order.get('symbol', 'N/A')
        side = "📈 BUY" if order.get('side') == 'BUY' else "📉 SELL"
        status = order.get('status', 'N/A')
        qty = float(order.get('origQty', 0))
        exec_qty = float(order.get('executedQty', 0))
        price = float(order.get('price', 0))
        timestamp = order.get('time', 0)
        
        # Convertir timestamp en date lisible
        try:
            date_str = datetime.fromtimestamp(int(timestamp) / 1000).strftime("%d/%m/%Y %H:%M:%S")
        except:
            date_str = str(timestamp)
        
        print(f"\n   [{i}] {symbol} {side} | {status}")
        print(f"       Cmd: {format_number(qty, 8)} | Exécutée: {format_number(exec_qty, 8)} | Prix: {format_number(price, 2)}")
        print(f"       Date: {date_str}")
    
    return len(displayed_orders)

# ==========================================
# FONCTION PRINCIPALE
# ==========================================

def generate_report() -> None:
    """Génère un rapport complet du portefeuille de trading."""
    
    if not API_KEY or not API_SECRET:
        print("❌ Clés API manquantes. Vérifiez config.json ou les variables d'environnement.")
        return
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    print_header(f"📊 RAPPORT TRADING - {timestamp}")
    
    # ===== PERPETUAL FUTURES =====
    print("\n🔄 Récupération des données Perpetual Futures...")
    swap_balance = get_swap_balance()
    perp_positions = get_swap_positions()
    
    # ===== STANDARD FUTURES =====
    print("\n" + "="*60)
    print("\n🔄 Récupération des données Standard Futures...")
    std_balance = get_standard_futures_balance()
    std_positions = get_standard_futures_positions()
    std_orders = get_standard_futures_orders(limit=5)
    
    # ===== RÉSUMÉ =====
    print_header("📈 RÉSUMÉ DU PORTEFEUILLE")
    
    total_balance = 0
    total_available = 0
    total_pnl = 0
    total_positions = perp_positions + std_positions
    
    if swap_balance:
        total_balance += float(swap_balance.get('balance', 0))
        total_available += float(swap_balance.get('availableMargin', 0))
        total_pnl += float(swap_balance.get('unrealizedProfit', 0))
    
    if std_balance:
        total_balance += float(std_balance.get('balance', 0))
        total_available += float(std_balance.get('available', 0))
        total_pnl += float(std_balance.get('unrealizedProfit', 0))
    
    print(f"\n💰 Solde Total:       {format_number(total_balance, 2)} USDT")
    print(f"💵 Disponible:        {format_number(total_available, 2)} USDT")
    print(f"📊 P&L Total:         {format_number(total_pnl, 4)} USDT")
    print(f"📍 Positions Ouvertes: {total_positions}")
    
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Temps d'exécution: {elapsed_time:.2f}s")
    print("\n✅ Rapport terminé.\n")

if __name__ == "__main__":
    generate_report()