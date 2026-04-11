# Living the Dream Trading 📈

> **Swing trading dashboard** — React + FastAPI + SQLite + Telegram alerts

Branch: `living-the-dream-v2` | Repo: `theobamboo/Dashboard-2026`

---

## Architecture

```
Frontend  (React + Tailwind + TradingView + D3.js)
    │  REST / WebSocket
    ▼
Backend   (FastAPI — Python)
    ├── engines/          ← one data engine per market
    ├── routers/          ← one API router per market
    ├── models.py         ← Pydantic schemas
    └── config.py         ← env-based settings
    │
    ├── SQLite            ← signals, alert history, cached responses
    └── APScheduler       ← timed jobs → Telegram Bot
```

## Market Pages

| Page | Data Sources | Key Components |
|---|---|---|
| **Crypto** | CoinGecko, CoinGlass, CryptoQuant, IntoTheBlock, Alternative.me | D3 bubble chart, liquidations heatmap, funding rates, Fear&Greed |
| **Stocks / ETFs** | yfinance, CBOE | TradingView chart, VIX panel, Put/Call ratio, screener |
| **Bonds / Macro** | FRED API, yfinance (DXY) | Yield curve, credit spreads, DXY overlay, central bank rates |
| **FX** | exchangerate.host, CFTC COT | Pair rates, COT positioning, carry ranking, correlation matrix |

---

## Development Layers

| Layer | Status | Description |
|---|---|---|
| **1** | ✅ Done | Project scaffold + FastAPI server |
| **2** | ⏳ Next | Data engines + live endpoints |
| **3** | ⏳ | SQLite schema + signal storage |
| **4** | ⏳ | Telegram alerts + APScheduler |
| **5** | ⏳ | React frontend — all 4 market pages |
| **6** | ⏳ | D3 bubble chart + liquidations heatmap |
| **7** | ⏳ | TradingView chart integration |
| **8** | ⏳ | Confluence signal engine |

---

## Quick Start (Layer 1)

### Prerequisites
- Python 3.11+
- Git

### Setup
```powershell
# 1. Clone & checkout branch
git clone https://github.com/theobamboo/Dashboard-2026.git
cd Dashboard-2026
git checkout living-the-dream-v2

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your API keys

# 5. Start server
uvicorn backend.main:app --reload --port 8000
```

### Verify
- **Health check**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/docs
- **Crypto endpoint**: http://localhost:8000/api/v1/crypto

---

## API Endpoints (Layer 1 stubs)

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Server liveness probe |
| `GET` | `/api/v1/crypto` | Crypto market overview |
| `GET` | `/api/v1/crypto/prices` | Top-N coin prices |
| `GET` | `/api/v1/crypto/funding-rates` | Perp funding rates |
| `GET` | `/api/v1/crypto/liquidations` | Liquidation heatmap data |
| `GET` | `/api/v1/crypto/fear-greed` | Fear & Greed index |
| `GET` | `/api/v1/stocks` | Stocks & ETFs overview |
| `GET` | `/api/v1/stocks/vix` | VIX data |
| `GET` | `/api/v1/stocks/put-call-ratio` | CBOE Put/Call ratio |
| `GET` | `/api/v1/bonds` | Bonds / macro overview |
| `GET` | `/api/v1/bonds/yield-curve` | US Treasury yield curve |
| `GET` | `/api/v1/bonds/dxy` | DXY Dollar Index |
| `GET` | `/api/v1/fx` | FX market overview |
| `GET` | `/api/v1/fx/rates` | Live exchange rates |
| `GET` | `/api/v1/fx/cot` | CFTC COT positioning |
