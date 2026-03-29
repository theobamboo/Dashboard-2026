import pandas as pd
import yfinance as yf
from pytrends.request import TrendReq
import time

class SocialEngine:
    def __init__(self):
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360, retries=2, backoff_factor=0.2)
        except:
            self.pytrends = None
            
    def get_social_pulse(self, ticker, market_type="Stocks"):
        """
        Calculates social dominance and engagement spikes.
        Returns dict with spike (bool) and dominance (float).
        """
        # Clean ticker to base asset name
        clean_keyword = ticker.split('=')[0].split('-')[0].split('/')[0] # AAPL or BTC
        if market_type == "Crypto" and clean_keyword != 'BTC' and clean_keyword != 'ETH':
            # Add ' crypto' to narrow trends, e.g., 'SOL crypto'
            search_term = f"{clean_keyword} crypto"
        else:
            search_term = clean_keyword

        # 1. Pytrends parsing
        try:
            if self.pytrends:
                self.pytrends.build_payload(kw_list=[search_term], timeframe='now 7-d')
                df = self.pytrends.interest_over_time()
                
                if not df.empty and search_term in df.columns:
                    recent = df[search_term].tail(31)
                    
                    if len(recent) > 1:
                        last_val = recent.iloc[-1] + 0.1 # avoid div by zero
                        hist = recent.iloc[:-1]
                        mean_val = hist.mean() + 0.1
                        
                        spike = last_val > (2 * mean_val)
                        dominance = min(last_val, 99.9) # trends is out of 100
                        
                        return {
                            'spike': spike, 
                            'dominance': dominance,
                            'source': 'Google Trends API'
                        }
        except Exception as e:
            print(f"[Social] pytrends throttled or failed: {e}")
            
        # 2. Proxy Fallback (StockTwits requires API keys for consistent pulls, so we use Volume Spikes as Social Proxy)
        try:
            target = ticker.replace('/', '') + '=X' if market_type == 'Forex' else ticker.replace('/', '-')
            if '/' in ticker and 'USD' in ticker:
                target = ticker.replace('/', '-').replace('USDT', 'USD')
                
            tkr = yf.Ticker(target)
            hist = tkr.history(period="1mo", interval="1d")
            
            if not hist.empty and 'Volume' in hist.columns:
                recent_vol = hist['Volume'].tail(31)
                if len(recent_vol) > 1:
                    last_vol = recent_vol.iloc[-1]
                    mean_vol = recent_vol.iloc[:-1].mean()
                    
                    spike = last_vol > (2 * mean_vol) if mean_vol > 0 else False
                    
                    # Calculate a relative synthetic "dominance" mapped 1 to 99
                    rel_ratio = last_vol / (mean_vol + 1)
                    dominance = max(1.0, min(rel_ratio * 30.0, 99.9))
                    
                    return {
                        'spike': spike,
                        'dominance': dominance,
                        'source': 'Volume/Social Proxy'
                    }
        except Exception as e:
             print(f"[Social] Volume proxy failed: {e}")
             
        # Deep fallback if all APIs are unresponsive
        return {
            'spike': False,
            'dominance': 8.4,
            'source': 'Offline'
        }
