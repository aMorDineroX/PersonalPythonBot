# PersonalPythonBot - BingX Trading Bot

This is a simple Python trading bot for BingX using Bollinger Bands and RSI indicators. It can run in test mode (no API keys required) or live mode (with your BingX API credentials).

## Features
- Fetches OHLCV data from BingX (or simulates data in test mode)
- Calculates Bollinger Bands (20, 2) and RSI (14)
- Generates BUY/SELL/HOLD signals
- Places real or simulated orders

## Requirements
- Python 3.8+
- Install dependencies:

```bash
pip install pandas pandas_ta requests
```

## Configuration

### 1. API Keys (for live trading)
- Add your BingX API key and secret to `config.json`:

```
{
    "BINGX_API_KEY": "your_api_key_here",
    "BINGX_API_SECRET": "your_api_secret_here"
}
```

- Or set them as environment variables:

```bash
export BINGX_API_KEY="your_api_key"
export BINGX_API_SECRET="your_api_secret"
```

### 2. Test Mode
- If you do not provide API keys, the bot will run in test mode using simulated data and will not place real orders.

## How to Run

```bash
python trading_bot.py
```

- The bot will print signals and (in live mode) place orders automatically.
- To stop the bot, press `Ctrl+C`.

## Notes
- For live trading, use at your own risk. Test thoroughly before using real funds.
- You can adjust trading parameters (symbol, interval, order size) in `trading_bot.py`.

## License
MIT
