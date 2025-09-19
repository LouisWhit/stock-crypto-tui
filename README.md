# Stock & Crypto TUI

A beautiful terminal user interface for displaying stock and cryptocurrency data in a grid layout. Built with Python and featuring real-time data, ASCII charts, and customizable styling.

## Features

- 📊 **Grid Layout**: Display up to 12 tickers in a 4-column grid
- 📈 **Real-time Data**: Live stock prices and crypto data
- 🎨 **Color Coding**: Green for gains, red for losses with directional arrows
- 📉 **ASCII Charts**: 3-month price trend visualization
- ⚙️ **Configurable**: Customize colors, symbols, and display options
- 🔄 **Watch Mode**: Auto-refresh every 30 seconds
- 🚀 **No Build Required**: Pure Python script, runs immediately

## Supported Assets

### Stocks
Any stock ticker supported by Yahoo Finance (e.g., AAPL, MSFT, GOOGL, TSLA)

### Cryptocurrencies
- BTC (Bitcoin)
- ETH (Ethereum) 
- ADA (Cardano)
- DOT (Polkadot)
- LINK (Chainlink)
- LTC (Litecoin)
- XRP (Ripple)
- DOGE (Dogecoin)
- SHIB (Shiba Inu)
- MATIC (Polygon)
- AVAX (Avalanche)
- SOL (Solana)

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd price
./setup.sh
```

### 2. Reload Shell
```bash
source ~/.bashrc
```

### 3. Run the Tool
```bash
# Single ticker
price AAPL

# Multiple tickers
price AAPL BTC ETH TSLA

# Watch mode (auto-refresh)
price --watch AAPL BTC ETH
```

## Manual Installation

If you prefer manual setup:

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Make Script Executable
```bash
chmod +x stock_crypto_tui.py
```

### 3. Create Alias
Add to your `~/.bashrc`:
```bash
alias price='python3 /path/to/price/stock_crypto_tui.py'
```

### 4. Reload Shell
```bash
source ~/.bashrc
```

## Configuration

Edit `config.json` to customize the appearance:

```json
{
  "colors": {
    "positive": "#00FF00",
    "negative": "#FF0000", 
    "neutral": "#FFFFFF",
    "ticker": "#00FFFF",
    "price": "#FFFFFF"
  },
  "display": {
    "max_tickers_per_row": 4,
    "max_tickers": 12,
    "chart_height": 8,
    "chart_width": 20
  },
  "symbols": {
    "up": "▲",
    "down": "▼"
  },
  "currency": {
    "default": "USD",
    "symbol": "$"
  }
}
```

### Color Options
- Use hex color codes (e.g., `#FF0000` for red, `#00FF00` for green)
- Common colors: `#FFFFFF` (white), `#000000` (black), `#FF0000` (red), `#00FF00` (green), `#0000FF` (blue), `#FFFF00` (yellow), `#FF00FF` (magenta), `#00FFFF` (cyan)

### Currency Options
- `default`: Currency code for API calls (USD, EUR, GBP, JPY, etc.)
- `symbol`: Currency symbol to display ($, €, £, ¥, etc.)

### Display Options
- `max_tickers_per_row`: Maximum tickers per row (default: 4)
- `max_tickers`: Maximum total tickers (default: 12)
- `chart_height`: ASCII chart height in lines (default: 8)
- `chart_width`: ASCII chart width in characters (default: 20)

## Usage Examples

```bash
# Stock portfolio
price AAPL MSFT GOOGL AMZN

# Crypto portfolio  
price BTC ETH ADA DOT

# Mixed portfolio
price AAPL BTC ETH TSLA

# Watch mode with custom config
price --config my_config.json --watch AAPL BTC

# Different currency (e.g., EUR)
# First update config.json: "default": "EUR", "symbol": "€"
price AAPL BTC ETH
```

## Data Sources

- **Stocks**: Yahoo Finance (via yfinance library)
- **Cryptocurrencies**: CoinGecko API
- **No API keys required** for basic usage

## Requirements

- Python 3.8 or higher
- Internet connection
- Terminal with color support

## Troubleshooting

### Common Issues

**"Command not found" after setup**
```bash
source ~/.bashrc
```

**"No module named 'yfinance'"**
```bash
pip3 install -r requirements.txt
```

**"Failed to fetch data"**
- Check internet connection
- Verify ticker symbols are correct
- Some tickers may not be available

**Colors not displaying**
- Ensure your terminal supports colors
- Try running with `TERM=xterm-256color price AAPL`

### Performance Tips

- Limit to 8-12 tickers for best performance
- Use watch mode sparingly to avoid API rate limits
- Close other network-intensive applications

## Security

- No API keys required for basic functionality
- All data fetched over HTTPS
- No sensitive data stored locally
- Script runs with user permissions only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please open an issue on GitHub.

---

**Enjoy tracking your investments in the terminal! 🚀📈**
