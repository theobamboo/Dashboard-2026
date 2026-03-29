import yfinance as yf
import requests
import feedparser
import time
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
]

class IntelEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def _score_headline(self, text):
        scores = self.analyzer.polarity_scores(text)
        comp = scores['compound']
        if comp > 0.05: return 1
        elif comp < -0.05: return -1
        return 0

    def _time_ago(self, ts):
        """Convert a Unix timestamp or datetime to '12m ago', '2h ago' etc."""
        try:
            if ts is None: return ""
            if isinstance(ts, (int, float)):
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            elif isinstance(ts, datetime):
                dt = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
            else:
                return ""
            diff = int((datetime.now(tz=timezone.utc) - dt).total_seconds())
            if diff < 60: return f"{diff}s ago"
            elif diff < 3600: return f"{diff // 60}m ago"
            elif diff < 86400: return f"{diff // 3600}h ago"
            else: return f"{diff // 86400}d ago"
        except:
            return ""

    def get_news_sentiment(self, ticker, market_type="Stocks"):
        all_news = []

        # --- SOURCE 1: yfinance ---
        clean_ticker = ticker.replace('/', '') + '=X' if market_type == 'Forex' else ticker.replace('/', '-')
        if '/' in ticker and 'USD' in ticker:
            clean_ticker = ticker.replace('/', '-').replace('USDT', 'USD')

        try:
            tkr = yf.Ticker(clean_ticker)
            yf_news = tkr.news
            if yf_news:
                for item in yf_news:
                    content = item.get('content', item)
                    title = content.get('title', '')
                    if not title: continue
                    link_obj = content.get('clickThroughUrl', {})
                    link = link_obj.get('url', content.get('link', ''))
                    pub_obj = content.get('provider', {})
                    publisher = pub_obj.get('displayName', content.get('publisher', 'Yahoo Finance'))
                    # Timestamp — yfinance uses 'providerPublishTime' (unix) or nested pubDate
                    pub_ts = content.get('pubDate', None)
                    if pub_ts and isinstance(pub_ts, str):
                        try:
                            from email.utils import parsedate_to_datetime
                            pub_ts = parsedate_to_datetime(pub_ts).timestamp()
                        except:
                            pub_ts = None
                    # fallback: top-level providerPublishTime
                    if pub_ts is None:
                        pub_ts = item.get('providerPublishTime', None)

                    score = self._score_headline(title)
                    all_news.append({
                        'title': title, 'link': link, 'source': publisher,
                        'score': score, 'time_ago': self._time_ago(pub_ts)
                    })
        except Exception as e:
            print(f"[Intel] yfinance failed for {ticker}: {e}")

        # --- SOURCE 2 & 3: Crypto-only ---
        if market_type == "Crypto":
            coin = ticker.split('/')[0] if '/' in ticker else ticker

            # CryptoPanic
            try:
                res = requests.get(f"https://cryptopanic.com/api/v1/posts/?currencies={coin}", timeout=3)
                if res.status_code == 200:
                    for post in res.json().get('results', [])[:10]:
                        title = post.get('title', '')
                        if not title: continue
                        created = post.get('created_at', None)
                        ts = None
                        if created:
                            try:
                                dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                                ts = dt.timestamp()
                            except: pass
                        score = self._score_headline(title)
                        all_news.append({
                            'title': title, 'link': post.get('url', ''), 'source': 'CryptoPanic',
                            'score': score, 'time_ago': self._time_ago(ts)
                        })
            except Exception as e:
                print(f"[Intel] CryptoPanic failed: {e}")

            # RSS Feeds
            for url in RSS_FEEDS:
                try:
                    feed = feedparser.parse(url)
                    added = 0
                    for entry in feed.entries:
                        if added >= 5: break
                        summary = entry.summary if hasattr(entry, 'summary') else ''
                        if coin.lower() in entry.title.lower() or coin.lower() in summary.lower():
                            ts = None
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                ts = time.mktime(entry.published_parsed)
                            score = self._score_headline(entry.title)
                            src = feed.feed.title if hasattr(feed.feed, 'title') else 'RSS'
                            all_news.append({
                                'title': entry.title, 'link': entry.link, 'source': src,
                                'score': score, 'time_ago': self._time_ago(ts)
                            })
                            added += 1
                except Exception as e:
                    print(f"[Intel] RSS failed: {e}")

        # Dedup
        seen = set()
        unique_news = []
        for n in all_news:
            if n['title'] not in seen:
                seen.add(n['title'])
                unique_news.append(n)

        total = len(unique_news)
        if total == 0:
            return {'news': [], 'outlook': "0% NEUTRAL", 'outlook_score': 0, 'pct': 0}

        bull_count = sum(1 for n in unique_news if n['score'] == 1)
        bear_count = sum(1 for n in unique_news if n['score'] == -1)
        neut_count = sum(1 for n in unique_news if n['score'] == 0)
        max_count = max(bull_count, bear_count, neut_count)
        pct = int((max_count / total) * 100)

        if max_count == bull_count and bull_count > 0: outlook = f"{pct}% BULLISH"; oscore = 1
        elif max_count == bear_count and bear_count > 0: outlook = f"{pct}% BEARISH"; oscore = -1
        else: outlook = f"{pct}% NEUTRAL"; oscore = 0

        return {'news': unique_news, 'outlook': outlook, 'outlook_score': oscore, 'pct': pct}
