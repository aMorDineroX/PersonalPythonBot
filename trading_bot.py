import pandas as pd
import pandas_ta as ta
import time
import os
import requests
import hmac
import hashlib
import base64
import json

# --- Indicator Calculation ---
def calculate_indicators(df):
    """
    Calculate Bollinger Bands (20, 2) and RSI (14).
    """
    bbands = ta.bbands(df['close'], length=20, std=2)
    df['lower_band'] = bbands[bbands.columns[0]]  # BBL_20_2.0
    df['upper_band'] = bbands[bbands.columns[2]]  # BBU_20_2.0
    df['rsi'] = ta.rsi(df['close'], length=14)
    return df

# --- Signal Generation ---
def generate_signal(df):
    """
    Volatility strategy (Bounce on bands)
    """
    if df.empty or len(df) < 21:
        return 'HOLD'
    last = df.iloc[-1]
    # LONG (BUY): Close below lower band and RSI < 35
    if last['close'] < last['lower_band'] and last['rsi'] < 35:
        return 'BUY'
    # SHORT (SELL): Close above upper band and RSI > 65
    elif last['close'] > last['upper_band'] and last['rsi'] > 65:
        return 'SELL'
    return 'HOLD'


# --- BingX API Integration ---

BINGX_API_URL = "https://open-api.bingx.com"

# --- Load API keys from config.json if not set in environment ---
def load_api_keys():
    api_key = os.getenv("BINGX_API_KEY")
    api_secret = os.getenv("BINGX_API_SECRET")
    if not api_key or not api_secret:
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                api_key = config.get("BINGX_API_KEY", api_key)
                api_secret = config.get("BINGX_API_SECRET", api_secret)
        except Exception as e:
            print("Could not load config.json:", e)
    return api_key, api_secret

BINGX_API_KEY, BINGX_API_SECRET = load_api_keys()

def fetch_bingx_ohlc(symbol='BTC-USDT', interval='1h', limit=100):
    """
    Fetch OHLCV data from BingX API. If no API keys, use simulated data for testing.
    """
    if not BINGX_API_KEY or not BINGX_API_SECRET:
        # Simulate random walk data for test mode
        import numpy as np
        np.random.seed(42)
        close = np.cumsum(np.random.randn(limit)) + 40000
        df = pd.DataFrame({'close': close})
        return df
    endpoint = f"/openApi/swap/v2/quote/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    url = BINGX_API_URL + endpoint
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        if data.get('code') == 0 and 'data' in data:
            df = pd.DataFrame(data['data'])
            df['close'] = df['close'].astype(float)
            return df
        else:
            print("BingX API error:", data)
    except Exception as e:
        print("Error fetching BingX data:", e)
    # fallback: return empty DataFrame
    return pd.DataFrame(columns=['close'])

def sign_bingx_request(params, secret):
    """
    Sign BingX API request parameters.
    """
    query = '&'.join([f"{k}={params[k]}" for k in sorted(params)])
    signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return signature

def place_bingx_order(symbol, side, quantity, price=None, order_type="MARKET"):
    """
    Place an order on BingX. If no API keys, just print simulated order for testing.
    """
    if not BINGX_API_KEY or not BINGX_API_SECRET:
        print(f"[TEST MODE] Would place {side} order for {quantity} {symbol} (no API keys)")
        return None
    endpoint = "/openApi/swap/v2/trade/order"
    url = BINGX_API_URL + endpoint
    params = {
        "symbol": symbol,
        "side": side,  # 'BUY' or 'SELL'
        "type": order_type,  # 'MARKET' or 'LIMIT'
        "quantity": str(quantity),
        "timestamp": str(int(time.time() * 1000)),
    }
    if price and order_type == "LIMIT":
        params["price"] = str(price)
    params["recvWindow"] = "5000"
    params["signature"] = sign_bingx_request(params, BINGX_API_SECRET)
    headers = {
        "X-BX-APIKEY": BINGX_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        resp = requests.post(url, data=params, headers=headers)
        data = resp.json()
        print("Order response:", data)
        return data
    except Exception as e:
        print("Order error:", e)
        return None

# --- Main Bot Loop ---

def main():
    symbol = 'BTC-USDT'  # BingX uses dash, not USDT
    interval = '1h'
    order_quantity = 0.001  # Example: 0.001 BTC
    while True:
        df = fetch_bingx_ohlc(symbol, interval)
        if df.empty:
            print("No data fetched. Retrying in 60 seconds...")
            time.sleep(60)
            continue
        df = calculate_indicators(df)
        signal = generate_signal(df)
        print(f"Signal for {symbol} ({interval}): {signal}")
        if signal == 'BUY':
            place_bingx_order(symbol, 'BUY', order_quantity)
        elif signal == 'SELL':
            place_bingx_order(symbol, 'SELL', order_quantity)
        # Wait for next interval
        time.sleep(60 * 60)  # 1 hour

if __name__ == "__main__":
    main()
