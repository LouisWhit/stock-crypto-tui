#!/usr/bin/env python3
"""
Stock & Crypto TUI - Terminal User Interface for displaying stock and cryptocurrency data
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich import box
import time

class StockCryptoTUI:
    def __init__(self, config_path: str = "config.json"):
        self.console = Console()
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "colors": {
                "positive": "#00FF00",
                "negative": "#FF0000",
                "neutral": "#FFFFFF",
                "ticker": "#00FFFF",
                "price": "#FFFFFF",
                "background": "#000000"
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
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for key, value in user_config.items():
                        if key in default_config and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                self.console.print(f"[red]Error loading config: {e}[/red]")
                self.console.print("[yellow]Using default configuration[/yellow]")
        
        return default_config
    
    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """Fetch stock data using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty:
                self.console.print(f"[yellow]No historical data available for {ticker}[/yellow]")
                return None
                
            # Get current price - try multiple sources
            current_price = None
            if 'currentPrice' in info and info['currentPrice'] is not None:
                current_price = info['currentPrice']
            elif 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                current_price = info['regularMarketPrice']
            elif 'previousClose' in info and info['previousClose'] is not None:
                current_price = info['previousClose']
            else:
                current_price = hist['Close'].iloc[-1]
            
            if current_price is None or current_price <= 0:
                self.console.print(f"[yellow]Invalid price data for {ticker}[/yellow]")
                return None
            
            # Calculate percentage changes
            changes = self.calculate_changes(hist, current_price)
            
            # Get Friday data for chart (last 3 months)
            friday_data = self.get_friday_data(hist)
            
            return {
                'ticker': ticker.upper(),
                'current_price': current_price,
                'changes': changes,
                'friday_data': friday_data,
                'type': 'stock'
            }
            
        except Exception as e:
            self.console.print(f"[red]Error fetching stock data for {ticker}: {e}[/red]")
            return None
    
    def get_crypto_data(self, ticker: str) -> Optional[Dict]:
        """Fetch cryptocurrency data using CoinGecko API"""
        try:
            # Map common crypto tickers to CoinGecko IDs
            crypto_mapping = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu',
                'MATIC': 'matic-network',
                'AVAX': 'avalanche-2',
                'SOL': 'solana',
                'HBAR': 'hedera-hashgraph',
            }
            
            coin_id = crypto_mapping.get(ticker.upper(), ticker.lower())
            
            # Get current data
            currency = self.config['currency']['default'].lower()
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': currency,
                'include_24hr_change': 'true',
                'include_7d_change': 'true',
                'include_30d_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if coin_id not in data:
                return None
                
            coin_data = data[coin_id]
            current_price = coin_data[currency]
            
            # Get historical data for YTD and chart
            hist_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            hist_params = {
                'vs_currency': currency,
                'days': '365',
                'interval': 'daily'
            }
            
            hist_response = requests.get(hist_url, params=hist_params, timeout=10)
            hist_response.raise_for_status()
            hist_data = hist_response.json()
            
            # Calculate YTD change
            ytd_change = self.calculate_ytd_change(hist_data['prices'], current_price)
            
            changes = {
                '24h': coin_data.get(f'{currency}_24h_change', 0),
                '7d': coin_data.get(f'{currency}_7d_change', 0),
                '30d': coin_data.get(f'{currency}_30d_change', 0),
                'ytd': ytd_change
            }
            
            # Get Friday data for chart
            friday_data = self.get_crypto_friday_data(hist_data['prices'])
            
            return {
                'ticker': ticker.upper(),
                'current_price': current_price,
                'changes': changes,
                'friday_data': friday_data,
                'type': 'crypto'
            }
            
        except Exception as e:
            self.console.print(f"[red]Error fetching crypto data for {ticker}: {e}[/red]")
            return None
    
    def calculate_changes(self, hist_data, current_price: float) -> Dict:
        """Calculate percentage changes for different time periods"""
        if hist_data.empty:
            return {'24h': 0, '7d': 0, '30d': 0, 'ytd': 0}
        
        changes = {}
        
        # 24h change
        if len(hist_data) >= 2:
            changes['24h'] = ((current_price - hist_data['Close'].iloc[-2]) / hist_data['Close'].iloc[-2]) * 100
        else:
            changes['24h'] = 0
            
        # 7d change
        if len(hist_data) >= 7:
            changes['7d'] = ((current_price - hist_data['Close'].iloc[-8]) / hist_data['Close'].iloc[-8]) * 100
        else:
            changes['7d'] = 0
            
        # 30d change
        if len(hist_data) >= 30:
            changes['30d'] = ((current_price - hist_data['Close'].iloc[-31]) / hist_data['Close'].iloc[-31]) * 100
        else:
            changes['30d'] = 0
            
        # YTD change
        current_year = datetime.now().year
        ytd_data = hist_data[hist_data.index.year == current_year]
        if not ytd_data.empty:
            changes['ytd'] = ((current_price - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0]) * 100
        else:
            # If no data for current year, use the first available data point
            if not hist_data.empty:
                changes['ytd'] = ((current_price - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0]) * 100
            else:
                changes['ytd'] = 0
            
        return changes
    
    def calculate_ytd_change(self, price_data: List, current_price: float) -> float:
        """Calculate YTD change for crypto"""
        if not price_data:
            return 0
            
        current_year = datetime.now().year
        year_start = datetime(current_year, 1, 1).timestamp() * 1000
        
        # Find the first price data point of the current year
        year_start_price = None
        for timestamp, price in price_data:
            if timestamp >= year_start:
                year_start_price = price
                break
                
        if year_start_price is None:
            return 0
            
        return ((current_price - year_start_price) / year_start_price) * 100
    
    def get_friday_data(self, hist_data) -> List[float]:
        """Get Friday closing prices for the last 3 months"""
        if hist_data.empty:
            return []
            
        try:
            # Get last 3 months of data
            three_months_ago = datetime.now() - timedelta(days=90)
            recent_data = hist_data[hist_data.index >= three_months_ago]
            
            # Filter for Fridays (weekday 4)
            friday_data = recent_data[recent_data.index.weekday == 4]
            
            # Return the last 12 Friday prices (approximately 3 months)
            if not friday_data.empty:
                return friday_data['Close'].tail(12).tolist()
            else:
                # If no Fridays found, return recent data points
                return recent_data['Close'].tail(12).tolist()
        except Exception:
            # Fallback: return recent data points
            return hist_data['Close'].tail(12).tolist()
    
    def get_crypto_friday_data(self, price_data: List) -> List[float]:
        """Get Friday prices for crypto (approximate)"""
        if not price_data:
            return []
            
        # Get last 3 months of data
        three_months_ago = datetime.now() - timedelta(days=90)
        three_months_ago_ts = three_months_ago.timestamp() * 1000
        
        recent_data = [(ts, price) for ts, price in price_data if ts >= three_months_ago_ts]
        
        # Sample every 7th data point to approximate weekly data
        friday_data = []
        for i in range(0, len(recent_data), 7):
            if len(friday_data) < 12:  # Limit to 12 data points
                friday_data.append(recent_data[i][1])
                
        return friday_data
    
    def create_ascii_chart(self, data: List[float], width: int = 20, height: int = 8) -> str:
        """Create ASCII chart from price data"""
        if not data or len(data) < 2:
            return "No data"
            
        min_price = min(data)
        max_price = max(data)
        price_range = max_price - min_price
        
        if price_range == 0:
            return "─" * width
            
        chart_lines = []
        
        # Create each line of the chart
        for i in range(height):
            line = ""
            threshold = max_price - (price_range * i / height)
            
            for price in data:
                if price >= threshold:
                    line += "█"
                else:
                    line += " "
                    
            chart_lines.append(line)
            
        return "\n".join(reversed(chart_lines))
    
    def format_price(self, price: float) -> str:
        """Format price with appropriate decimal places"""
        currency_symbol = self.config['currency']['symbol']
        if price >= 1000:
            return f"{currency_symbol}{price:,.2f}"
        elif price >= 1:
            return f"{currency_symbol}{price:.2f}"
        else:
            return f"{currency_symbol}{price:.4f}"
    
    def format_change(self, change: float) -> Tuple[str, str]:
        """Format percentage change with color and symbol"""
        if change > 0:
            color = self.config['colors']['positive']
            symbol = self.config['symbols']['up']
        elif change < 0:
            color = self.config['colors']['negative']
            symbol = self.config['symbols']['down']
        else:
            color = self.config['colors']['neutral']
            symbol = " "
            
        formatted_change = f"{symbol}{abs(change):.2f}%"
        return formatted_change, color
    
    def create_ticker_panel(self, data: Dict) -> Panel:
        """Create a panel for a single ticker"""
        # Ticker symbol
        ticker_text = Text(data['ticker'], style=self.config['colors']['ticker'])
        
        # Current price
        price_text = Text(self.format_price(data['current_price']), 
                         style=self.config['colors']['price'])
        
        # Changes table
        changes_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        changes_table.add_column("24h", justify="center")
        changes_table.add_column("7d", justify="center")
        changes_table.add_column("30d", justify="center")
        changes_table.add_column("YTD", justify="center")
        
        row_data = []
        for period in ['24h', '7d', '30d', 'ytd']:
            change, color = self.format_change(data['changes'][period])
            row_data.append(Text(change, style=color))
            
        changes_table.add_row(*row_data)
        
        # ASCII chart
        chart = self.create_ascii_chart(data['friday_data'], 
                                      self.config['display']['chart_width'],
                                      self.config['display']['chart_height'])
        
        # Create a simple text-based content
        content = f"{ticker_text}\n{price_text}\n\n"
        
        # Add table as rendered text
        from io import StringIO
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        self.console.print(changes_table)
        sys.stdout = old_stdout
        table_text = buffer.getvalue()
        
        content += table_text + "\n" + chart
        
        return Panel(
            content,
            title=f"{data['type'].title()} Data",
            border_style="blue",
            padding=(1, 1)
        )
    
    def display_grid(self, tickers: List[str]):
        """Display tickers in a grid layout"""
        self.console.clear()
        
        # Fetch data for all tickers
        data_list = []
        for ticker in tickers:
            if ticker.upper() in ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'LTC', 'XRP', 'DOGE', 'SHIB', 'MATIC', 'AVAX', 'SOL']:
                data = self.get_crypto_data(ticker)
            else:
                data = self.get_stock_data(ticker)
                
            if data:
                data_list.append(data)
            else:
                self.console.print(f"[red]Failed to fetch data for {ticker}[/red]")
        
        if not data_list:
            self.console.print("[red]No data available for any tickers[/red]")
            return
        
        # Create grid layout
        max_per_row = self.config['display']['max_tickers_per_row']
        panels = []
        
        for data in data_list:
            panels.append(self.create_ticker_panel(data))
        
        # Display in rows
        for i in range(0, len(panels), max_per_row):
            row_panels = panels[i:i + max_per_row]
            self.console.print(*row_panels)
            self.console.print()  # Empty line between rows
    
    def run(self, tickers: List[str]):
        """Main execution function"""
        if len(tickers) > self.config['display']['max_tickers']:
            self.console.print(f"[red]Maximum {self.config['display']['max_tickers']} tickers allowed[/red]")
            return
            
        self.display_grid(tickers)

def main():
    parser = argparse.ArgumentParser(description='Stock & Crypto TUI - Terminal display for financial data')
    parser.add_argument('tickers', nargs='+', help='Stock or crypto tickers to display')
    parser.add_argument('--config', '-c', default='config.json', help='Path to configuration file')
    parser.add_argument('--watch', '-w', action='store_true', help='Watch mode - refresh every 30 seconds')
    
    args = parser.parse_args()
    
    tui = StockCryptoTUI(args.config)
    
    if args.watch:
        try:
            while True:
                tui.run(args.tickers)
                time.sleep(30)
        except KeyboardInterrupt:
            tui.console.print("\n[yellow]Exiting watch mode...[/yellow]")
    else:
        tui.run(args.tickers)

if __name__ == "__main__":
    main()
