import ccxt
import yfinance as yf
import pandas as pd
import requests

# Spot ribbon tickers (always fetched)
RIBBON_TICKERS = {
    'BTC':     'BTC/USDT',
    'ETH':     'ETH/USDT',
    'SOL':     'SOL/USDT',
    'AAPL':    'AAPL',
    'NVDA':    'NVDA',
    'GOLD':    'GC=F',
    'EUR/USD': 'EURUSD=X',
    'DXY':     'DX-Y.NYB',
    'XAU/USD': 'GC=F',
}

# Subset for movers scanning
CRYPTO_MOVERS_UNIVERSE = [
    'BTC/USDT','ETH/USDT','SOL/USDT','BNB/USDT','XRP/USDT','ADA/USDT',
    'AVAX/USDT','DOGE/USDT','DOT/USDT','TRX/USDT','LINK/USDT','MATIC/USDT',
    'SHIB/USDT','LTC/USDT','BCH/USDT','UNI/USDT','ATOM/USDT','INJ/USDT',
    'APT/USDT','NEAR/USDT','ARB/USDT','OP/USDT','RNDR/USDT','FIL/USDT',
    'FTM/USDT','AAVE/USDT','SUI/USDT','SEI/USDT','PEPE/USDT','WLD/USDT',
]

STOCK_MOVERS_UNIVERSE = [
    'AAPL','MSFT','NVDA','AMZN','GOOGL','META','TSLA','BRK-B','LLY','V',
    'JPM','WMT','MA','UNH','AVGO','PG','JNJ','XOM','HD','ORCL','AMD',
    'NFLX','CRM','BA','INTC','DIS','QCOM','MU','PANW','BKNG',
]

FOREX_MOVERS_UNIVERSE = [
    'EURUSD=X','USDJPY=X','GBPUSD=X','AUDUSD=X','USDCAD=X','USDCHF=X',
    'NZDUSD=X','EURGBP=X','EURJPY=X','GBPJPY=X','CHFJPY=X','AUDJPY=X',
    'EURCAD=X','AUDCAD=X',
]

# Timeframe mapping
CRYPTO_TF_MAP = {
    '1h': '1h', '4h': '4h', '8h': '8h', '12h': '12h',
    '1D': '1d', '3D': '3d', '1W': '1w', '1M': '1M'
}
EQUITY_TF_MAP = {
    '1h': ('5d', '1h'), '4h': ('1mo', '1h'), '8h': ('1mo', '1h'),
    '12h': ('1mo', '1h'), '1D': ('6mo', '1d'), '3D': ('1y', '1d'),
    '1W': ('2y', '1wk'), '1M': ('5y', '1mo')
}


class DataEngine:
    def __init__(self):
        self.exchange = ccxt.binance()

    def fetch_crypto_candles(self, ticker, timeframe='1h', limit=100):
        try:
            tf = CRYPTO_TF_MAP.get(timeframe, '1h')
            ohlcv = self.exchange.fetch_ohlcv(ticker, timeframe=tf, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"[Error] fetch_crypto_candles: {e}")
            return pd.DataFrame()

    def fetch_equity_candles(self, ticker, timeframe='1h', limit=100):
        try:
            period, interval = EQUITY_TF_MAP.get(timeframe, ('1mo', '1h'))
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if not df.empty:
                if 'Close' in df.columns:
                    df = df.tail(limit)
                    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df.rename(columns=lambda x: str(x).lower(), inplace=True)
                    return df
                elif 'close' in df.columns:
                    return df.tail(limit)
            return pd.DataFrame()
        except Exception as e:
            print(f"[Error] fetch_equity_candles: {e}")
            return pd.DataFrame()

    def fetch_candles(self, ticker, timeframe='1h', limit=100):
        if "/" in ticker:
            return self.fetch_crypto_candles(ticker, timeframe, limit)
        else:
            return self.fetch_equity_candles(ticker, timeframe, limit)

    def get_ribbon_prices(self):
        """Fetch spot prices for the top ribbon marquee."""
        prices = {}
        for label, ticker in RIBBON_TICKERS.items():
            try:
                if '/' in ticker:
                    t = self.exchange.fetch_ticker(ticker)
                    prices[label] = {'price': t['last'], 'change': t.get('percentage', 0) or 0}
                else:
                    tk = yf.Ticker(ticker)
                    info = tk.fast_info
                    price = info.get('lastPrice', 0) or info.get('previousClose', 0)
                    prev = info.get('previousClose', price)
                    chg = ((price - prev) / prev * 100) if prev else 0
                    prices[label] = {'price': price, 'change': round(chg, 2)}
            except Exception as e:
                print(f"[Ribbon] {label} failed: {e}")
                prices[label] = {'price': 0, 'change': 0}
        return prices

    def get_market_movers(self, market_type="Crypto"):
        """Return top 7 gainers and losers for the selected market."""
        results = []

        if market_type == "Crypto":
            for sym in CRYPTO_MOVERS_UNIVERSE:
                try:
                    t = self.exchange.fetch_ticker(sym)
                    results.append({
                        'symbol': sym.split('/')[0],
                        'price': t['last'],
                        'change': t.get('percentage', 0) or 0
                    })
                except:
                    pass
        elif market_type == "Stocks":
            try:
                syms = ' '.join(STOCK_MOVERS_UNIVERSE)
                data = yf.download(syms, period='2d', interval='1d', group_by='ticker', progress=False)
                for sym in STOCK_MOVERS_UNIVERSE:
                    try:
                        if sym in data.columns.get_level_values(0):
                            sub = data[sym]
                        else:
                            sub = data
                        if len(sub) >= 2:
                            prev = sub['Close'].iloc[-2]
                            curr = sub['Close'].iloc[-1]
                            chg = ((curr - prev) / prev * 100) if prev else 0
                            # Handle potential Series/scalar
                            if hasattr(chg, 'iloc'): chg = chg.iloc[0]
                            if hasattr(curr, 'iloc'): curr = curr.iloc[0]
                            results.append({'symbol': sym, 'price': round(float(curr), 2), 'change': round(float(chg), 2)})
                    except:
                        pass
            except Exception as e:
                print(f"[Movers] Stock batch failed: {e}")
        else:
            # Forex
            try:
                syms = ' '.join(FOREX_MOVERS_UNIVERSE)
                data = yf.download(syms, period='2d', interval='1d', group_by='ticker', progress=False)
                for sym in FOREX_MOVERS_UNIVERSE:
                    try:
                        clean = sym.replace('=X', '')
                        if sym in data.columns.get_level_values(0):
                            sub = data[sym]
                        else:
                            sub = data
                        if len(sub) >= 2:
                            prev = sub['Close'].iloc[-2]
                            curr = sub['Close'].iloc[-1]
                            chg = ((curr - prev) / prev * 100) if prev else 0
                            if hasattr(chg, 'iloc'): chg = chg.iloc[0]
                            if hasattr(curr, 'iloc'): curr = curr.iloc[0]
                            results.append({'symbol': clean, 'price': round(float(curr), 4), 'change': round(float(chg), 2)})
                    except:
                        pass
            except Exception as e:
                print(f"[Movers] Forex batch failed: {e}")

        results.sort(key=lambda x: x['change'], reverse=True)
        gainers = results[:7]
        losers = results[-7:][::-1] if len(results) >= 7 else results[-len(results):][::-1]
        return {'gainers': gainers, 'losers': losers}

    def get_global_health(self):
        """Fetch Crypto Fear & Greed Index + BTC Dominance."""
        data = {}
        # Fear & Greed Index
        try:
            res = requests.get("https://api.alternative.me/fng/?limit=1", timeout=4)
            if res.status_code == 200:
                fng = res.json()['data'][0]
                data['fng_value'] = int(fng['value'])
                data['fng_label'] = fng['value_classification']
        except Exception as e:
            print(f"[Global] Fear & Greed failed: {e}")
            data['fng_value'] = None
            data['fng_label'] = "N/A"

        # BTC Dominance via CoinGecko public /global
        try:
            res = requests.get("https://api.coingecko.com/api/v3/global", timeout=5)
            if res.status_code == 200:
                g = res.json().get('data', {})
                btc_dom = g.get('market_cap_percentage', {}).get('btc', None)
                data['btc_dominance'] = round(btc_dom, 2) if btc_dom else None
                mktcap = g.get('total_market_cap', {}).get('usd', None)
                data['total_marketcap'] = f"${mktcap/1e12:.2f}T" if mktcap else "N/A"
            else:
                data['btc_dominance'] = None
                data['total_marketcap'] = "N/A"
        except Exception as e:
            print(f"[Global] CoinGecko failed: {e}")
            data['btc_dominance'] = None
            data['total_marketcap'] = "N/A"

        return data

    def get_derivatives_data(self, ticker):
        """
        Fetch Open Interest and Funding Rate for a crypto perpetual futures ticker.
        Uses Binance public REST API — no API key required.
        Returns dict: {oi, oi_change_24h, funding_rate, source}
        """
        result = {
            'oi':             None,
            'oi_change_24h':  None,
            'funding_rate':   None,
            'source':         'N/A',
        }
        if '/' not in ticker:
            return result  # Not crypto

        # Convert 'BTC/USDT' -> 'BTCUSDT'
        symbol = ticker.replace('/', '')

        # 1. Open Interest (current)
        try:
            url = f'https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}'
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                data = res.json()
                result['oi'] = float(data.get('openInterest', 0))
                result['source'] = 'Binance Futures'
        except Exception as e:
            print(f'[Deriv] OI fetch failed: {e}')

        # 2. OI History (24h change)
        try:
            url = ('https://fapi.binance.com/futures/data/openInterestHist'
                   f'?symbol={symbol}&period=1h&limit=25')
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                hist = res.json()
                if len(hist) >= 2:
                    oi_now  = float(hist[-1]['sumOpenInterest'])
                    oi_24h  = float(hist[0]['sumOpenInterest'])
                    if oi_24h > 0:
                        result['oi_change_24h'] = round((oi_now - oi_24h) / oi_24h * 100, 2)
        except Exception as e:
            print(f'[Deriv] OI history failed: {e}')

        # 3. Predicted Funding Rate
        try:
            url = f'https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}'
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                data = res.json()
                fr = float(data.get('lastFundingRate', 0))
                result['funding_rate'] = round(fr * 100, 4)  # Convert to % with 4dp
        except Exception as e:
            print(f'[Deriv] Funding rate failed: {e}')

        return result
