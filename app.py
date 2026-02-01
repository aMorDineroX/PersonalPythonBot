"""
BingX Trading Web Application - Backend API
FastAPI server pour le trading et le monitoring
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import hmac
import hashlib
import time
import requests
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

app = FastAPI(title="BingX Trading Bot", version="3.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINGX_API_URL = "https://open-api.bingx.com"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# ==========================================
# MODELS
# ==========================================

class APIKeys(BaseModel):
    api_key: str
    api_secret: str

class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY ou SELL
    quantity: float
    account_type: str  # swap ou contract

class PositionRequest(BaseModel):
    symbol: str
    account_type: str

class ClosePositionRequest(BaseModel):
    symbol: str
    account_type: str
    position_id: Optional[str] = None

# ==========================================
# GLOBAL STATE
# ==========================================

def load_config():
    """Charge les clés API depuis config.json"""
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
                return {
                    "api_key": config.get("BINGX_API_KEY", ""),
                    "api_secret": config.get("BINGX_API_SECRET", "")
                }
    except Exception as e:
        print(f"Erreur lors de la lecture de config.json: {e}")
    
    return {"api_key": "", "api_secret": ""}

current_keys: Dict[str, str] = load_config()

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def sign_request(params: Dict, secret: str) -> str:
    """Signe une requête avec HMAC SHA256"""
    query = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return signature

def safe_api_call(endpoint: str, params: Dict = None, method: str = "GET") -> Optional[Dict]:
    """Effectue un appel API BingX avec retry automatique"""
    if not current_keys["api_key"] or not current_keys["api_secret"]:
        raise HTTPException(status_code=401, detail="Clés API non configurées")
    
    if params is None:
        params = {}
    
    params["timestamp"] = str(int(time.time() * 1000))
    params["signature"] = sign_request(params, current_keys["api_secret"])
    
    headers = {"X-BX-APIKEY": current_keys["api_key"]}
    
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                response = requests.get(
                    BINGX_API_URL + endpoint,
                    params=params,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            elif method == "POST":
                response = requests.post(
                    BINGX_API_URL + endpoint,
                    json=params,
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
                time.sleep(1)
            else:
                raise HTTPException(status_code=504, detail="API Timeout")
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
            else:
                raise HTTPException(status_code=502, detail=f"Erreur API: {str(e)}")
    
    return None

def format_number(num: float, decimals: int = 2) -> str:
    """Formate un nombre avec séparateurs"""
    try:
        return f"{float(num):,.{decimals}f}"
    except:
        return str(num)

# ==========================================
# ENDPOINTS - CONFIGURATION
# ==========================================

@app.post("/api/config")
async def configure_keys(keys: APIKeys):
    """Configure les clés API BingX"""
    if not keys.api_key or not keys.api_secret:
        raise HTTPException(status_code=400, detail="Clés API manquantes")
    
    current_keys["api_key"] = keys.api_key
    current_keys["api_secret"] = keys.api_secret
    
    # Test la connexion
    try:
        result = safe_api_call("/openApi/swap/v2/user/balance")
        if isinstance(result, dict) and result.get('code') == 0:
            return {"status": "success", "message": "Clés API configurées et testées"}
        else:
            return {"status": "error", "message": "Clés API invalides"}
    except:
        return {"status": "error", "message": "Erreur de connexion à BingX"}

@app.get("/api/status")
async def get_status():
    """Vérifie l'état de la connexion API"""
    if not current_keys["api_key"]:
        return {"connected": False, "message": "Clés API non configurées"}
    
    try:
        result = safe_api_call("/openApi/swap/v2/user/balance")
        if isinstance(result, dict) and result.get('code') == 0:
            return {"connected": True, "message": "Connecté"}
        else:
            return {"connected": False, "message": "Erreur de connexion"}
    except:
        return {"connected": False, "message": "Erreur API"}

# ==========================================
# HELPER FUNCTIONS - BALANCE & POSITIONS
# ==========================================

async def fetch_perpetual_balance():
    """Helper: Récupère le solde Perpetual Futures"""
    endpoint = "/openApi/swap/v2/user/balance"
    data = safe_api_call(endpoint)
    
    if not data or data.get('code') != 0:
        print(f"[ERROR] Perpetual balance error: {data}")
        return None
    
    balance_data = data.get('data', {}).get('balance', {})
    
    return {
        "type": "perpetual",
        "balance": float(balance_data.get('balance', 0)),
        "available": float(balance_data.get('availableMargin', 0)),
        "pnl": float(balance_data.get('unrealizedProfit', 0))
    }

async def fetch_standard_balance():
    """Helper: Récupère le solde Standard Futures"""
    endpoint = "/openApi/contract/v1/balance"
    data = safe_api_call(endpoint)
    
    if not data or data.get('code') != 0:
        print(f"[ERROR] Standard balance error: {data}")
        return None
    
    balance_list = data.get('data', [])
    if isinstance(balance_list, list) and len(balance_list) > 0:
        balance_data = balance_list[0]
    else:
        balance_data = {}
    
    return {
        "type": "standard",
        "balance": float(balance_data.get('balance', 0)),
        "available": float(balance_data.get('available', 0)),
        "pnl": float(balance_data.get('unrealizedProfit', 0))
    }

async def fetch_perpetual_positions():
    """Helper: Récupère les positions Perpetual Futures"""
    endpoint = "/openApi/swap/v2/user/positions"
    data = safe_api_call(endpoint)
    
    if not data or data.get('code') != 0:
        print(f"[ERROR] Perpetual positions error: {data}")
        return {"type": "perpetual", "positions": [], "count": 0}
    
    positions_list = data.get('data', [])
    open_positions = [p for p in positions_list if float(p.get('positionAmt', 0)) != 0]
    
    positions = []
    for pos in open_positions:
        pos_side = pos.get('positionSide', '').upper()
        side = "LONG" if pos_side == "LONG" else "SHORT"
        
        positions.append({
            "symbol": pos.get('symbol'),
            "side": side,
            "amount": float(pos.get('positionAmt', 0)),
            "entry_price": float(pos.get('entryPrice', 0)),
            "current_price": float(pos.get('markPrice', 0)),
            "pnl": float(pos.get('unrealizedProfit', 0)),
            "leverage": float(pos.get('leverage', 1)),
            "margin": float(pos.get('margin', 0))
        })
    
    return {"type": "perpetual", "positions": positions, "count": len(positions)}

async def fetch_standard_positions():
    """Helper: Récupère les positions Standard Futures"""
    endpoint = "/openApi/contract/v1/allPosition"
    data = safe_api_call(endpoint)
    
    if not data or data.get('code') != 0:
        print(f"[ERROR] Standard positions error: {data}")
        return {"type": "standard", "positions": [], "count": 0}
    
    positions_list = data.get('data', [])
    open_positions = [p for p in positions_list if float(p.get('positionAmt', 0)) != 0]
    
    positions = []
    for pos in open_positions:
        pos_side = pos.get('positionSide', '').upper()
        side = "LONG" if pos_side == "LONG" else "SHORT"
        
        positions.append({
            "symbol": pos.get('symbol'),
            "side": side,
            "amount": float(pos.get('positionAmt', 0)),
            "entry_price": float(pos.get('entryPrice', 0)),
            "current_price": float(pos.get('currentPrice', 0)),
            "pnl": float(pos.get('unrealizedProfit', 0)),
            "leverage": float(pos.get('leverage', 1)),
            "margin": float(pos.get('margin', 0))
        })
    
    return {"type": "standard", "positions": positions, "count": len(positions)}

# ==========================================
# ENDPOINTS - BALANCE & POSITIONS
# ==========================================

@app.get("/api/balance/perpetual")
async def get_perpetual_balance():
    """Récupère le solde Perpetual Futures"""
    result = await fetch_perpetual_balance()
    if not result:
        raise HTTPException(status_code=400, detail="Erreur Perpetual")
    return result

@app.get("/api/balance/standard")
async def get_standard_balance():
    """Récupère le solde Standard Futures"""
    result = await fetch_standard_balance()
    if not result:
        raise HTTPException(status_code=400, detail="Erreur Standard Futures")
    return result

@app.get("/api/positions/perpetual")
async def get_perpetual_positions():
    """Récupère les positions Perpetual Futures"""
    return await fetch_perpetual_positions()

@app.get("/api/positions/standard")
async def get_standard_positions():
    """Récupère les positions Standard Futures"""
    return await fetch_standard_positions()

# ==========================================
# ENDPOINTS - STATISTIQUES AVANCÉES
# ==========================================

@app.get("/api/stats/summary")
async def get_stats_summary():
    """Récupère les statistiques P&L avancées"""
    try:
        perpetual = await fetch_perpetual_positions()
        standard = await fetch_standard_positions()
        
        all_positions = perpetual["positions"] + standard["positions"]
        
        # Calcul des statistiques
        total_pnl = sum(p["pnl"] for p in all_positions)
        total_margin = sum(p["margin"] for p in all_positions)
        winning = sum(1 for p in all_positions if p["pnl"] > 0)
        losing = sum(1 for p in all_positions if p["pnl"] < 0)
        
        # Agrégation par symbole
        symbols_agg = {}
        for pos in all_positions:
            sym = pos["symbol"]
            if sym not in symbols_agg:
                symbols_agg[sym] = {"pnl": 0, "positions": 0, "long": 0, "short": 0}
            symbols_agg[sym]["pnl"] += pos["pnl"]
            symbols_agg[sym]["positions"] += 1
            if pos["side"] == "LONG":
                symbols_agg[sym]["long"] += 1
            else:
                symbols_agg[sym]["short"] += 1
        
        perpetual_bal = await fetch_perpetual_balance()
        standard_bal = await fetch_standard_balance()
        
        # Debug: afficher les balances individuelles
        print(f"[DEBUG] Perpetual balance: {perpetual_bal}")
        print(f"[DEBUG] Standard balance: {standard_bal}")
        
        perp_balance = perpetual_bal["balance"] if perpetual_bal else 0
        std_balance = standard_bal["balance"] if standard_bal else 0
        
        return {
            "total_pnl": total_pnl,
            "total_positions": len(all_positions),
            "perpetual_pnl": sum(p["pnl"] for p in perpetual["positions"]),
            "standard_pnl": sum(p["pnl"] for p in standard["positions"]),
            "winning_count": winning,
            "losing_count": losing,
            "win_rate": f"{(winning / len(all_positions) * 100):.1f}%" if all_positions else "0%",
            "total_margin": total_margin,
            "perpetual_balance": perp_balance,
            "standard_balance": std_balance,
            "total_balance": perp_balance + std_balance,
            "symbols": symbols_agg
        }
    except Exception as e:
        print(f"[ERROR] get_stats_summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur stats: {str(e)}")

@app.get("/api/orders/history")
async def get_orders_history(limit: int = 50):
    """Récupère l'historique des ordres Standard Futures"""
    try:
        endpoint = "/openApi/contract/v1/allOrders"
        params = {"limit": limit}
        data = safe_api_call(endpoint, params)
        
        if not data or data.get('code') != 0:
            raise HTTPException(status_code=400, detail="Erreur historique")
        
        orders = data.get('data', [])
        
        formatted_orders = []
        for order in orders[:limit]:
            formatted_orders.append({
                "orderId": order.get('orderId'),
                "symbol": order.get('symbol'),
                "side": order.get('side'),
                "price": float(order.get('price', 0)),
                "quantity": float(order.get('origQty', 0)),
                "status": order.get('status'),
                "createTime": order.get('createTime'),
                "pnl": float(order.get('unrealizedProfit', 0))
            })
        
        return {"orders": formatted_orders, "count": len(formatted_orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur historique: {str(e)}")

# ==========================================
# ENDPOINTS - TRADING (À IMPLÉMENTER)
# ==========================================

@app.post("/api/trade/order")
async def place_order(order: OrderRequest):
    """Place un ordre (non-implémenté pour la sécurité)"""
    # Cette fonction nécessite une confirmation 2FA pour la sécurité
    return {"status": "pending", "message": "Fonction de trading non disponible pour le moment. Utilisez BingX directement."}

@app.post("/api/trade/close")
async def close_position(close_req: ClosePositionRequest):
    """Ferme une position (non-implémenté pour la sécurité)"""
    return {"status": "pending", "message": "Fonction de fermeture non disponible pour le moment. Utilisez BingX directement."}

# ==========================================
# ENDPOINTS - FRONTEND
# ==========================================

@app.get("/")
async def serve_index():
    """Serve l'application web"""
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health_check():
    """Vérification de santé"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
