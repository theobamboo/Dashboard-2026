import streamlit as st
import pandas as pd
import time
from engine.data_engine import DataEngine
from engine.smc_engine import SMCEngine
from engine.intel_engine import IntelEngine
from engine.social_engine import SocialEngine
from engine.universe import STOCKS_100, CRYPTO_100, FOREX_20
import plotly.graph_objects as go

st.set_page_config(page_title="Antigravity Terminal", layout="wide", initial_sidebar_state="expanded")

def load_css():
    try:
        with open('styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except: pass
load_css()

# --- ENGINE INIT (versioned to bust stale cache_resource) ---
@st.cache_resource
def get_data_engine_v4(): return DataEngine()
@st.cache_resource
def get_smc_engine_v3(): return SMCEngine()
@st.cache_resource
def get_intel_engine_v5(): return IntelEngine()
@st.cache_resource
def get_social_engine_v4(): return SocialEngine()

engine = get_data_engine_v4()
smc    = get_smc_engine_v3()
intel  = get_intel_engine_v5()
social = get_social_engine_v4()

# --- CACHED FETCHERS ---
@st.cache_data(ttl=60,  show_spinner=False)
def fetch_candles_cached(ticker, tf, limit):  return engine.fetch_candles(ticker, tf, limit)
@st.cache_data(ttl=60,  show_spinner=False)
def fetch_intel_cached(ticker, mt):          return intel.get_news_sentiment(ticker, mt)
@st.cache_data(ttl=60,  show_spinner=False)
def fetch_social_cached(ticker, mt):         return social.get_social_pulse(ticker, mt)
@st.cache_data(ttl=120, show_spinner=False)
def fetch_ribbon_cached():                   return engine.get_ribbon_prices()
@st.cache_data(ttl=120, show_spinner=False)
def fetch_movers_cached(mt):                 return engine.get_market_movers(mt)
@st.cache_data(ttl=300, show_spinner=False)
def fetch_global_health_cached():            return engine.get_global_health()
@st.cache_data(ttl=30,  show_spinner=False)
def fetch_derivatives_cached(ticker):        return engine.get_derivatives_data(ticker)

sys_logs = []

# =====================================================================
# SECTION 1 — SPOT PRICE RIBBON
# =====================================================================
ribbon = fetch_ribbon_cached()
if ribbon:
    sys_logs.append("[SUCCESS] RIBBON_LIVE")
    items_html = ""
    for label, data in ribbon.items():
        p   = data['price']
        c   = data['change']
        cls = "pos" if c >= 0 else "neg"
        sgn = "+" if c >= 0 else ""
        ps  = f"{p:,.2f}" if p > 10 else f"{p:.4f}"
        items_html += (f'<span class="ribbon-item"><span class="lbl">{label}</span>'
                       f'{ps} <span class="{cls}">{sgn}{c:.2f}%</span></span>')
    st.markdown(f'''
    <div class="ribbon-container">
        <div class="ribbon-track">{items_html}{items_html}</div>
    </div>''', unsafe_allow_html=True)
    st.markdown("<div style='font-family:monospace; font-size:10px; color:#555; text-align:right; margin-top:2px; padding-right:8px;'>[DXY_CORRELATION: INVERSE] &nbsp;|&nbsp; DXY ↑ → Risk Assets ↓</div>", unsafe_allow_html=True)
else:
    sys_logs.append("[WARNING] RIBBON_TIMEOUT")

# =====================================================================
# SECTION 2 — GLOBAL HEALTH INDICATORS
# =====================================================================
gh = fetch_global_health_cached()
fng_val   = gh.get('fng_value')
fng_lbl   = gh.get('fng_label', 'N/A')
btc_dom   = gh.get('btc_dominance')
total_mcap = gh.get('total_marketcap', 'N/A')

# Fear & Greed color mapping
if fng_val is not None:
    if fng_val >= 75:   fng_color = "#00D1FF"
    elif fng_val >= 55: fng_color = "#00D1FF"
    elif fng_val >= 45: fng_color = "#888888"
    elif fng_val >= 25: fng_color = "#FF4B4B"
    else:               fng_color = "#FF4B4B"
    fng_str = f"{fng_val} — {fng_lbl}"
    sys_logs.append(f"[SUCCESS] GLOBAL_HEALTH_LIVE")
else:
    fng_color = "#888"; fng_str = "N/A"

gh_cols = st.columns(4)
with gh_cols[0]:
    st.markdown(f"""<div class="mover-box">
        <div style="color:#888; font-size:10px;">FEAR & GREED</div>
        <div style="color:{fng_color}; font-size:16px; font-weight:bold;">{fng_str}</div>
    </div>""", unsafe_allow_html=True)
with gh_cols[1]:
    dom_str = f"{btc_dom:.1f}%" if btc_dom else "N/A"
    st.markdown(f"""<div class="mover-box">
        <div style="color:#888; font-size:10px;">BTC DOMINANCE</div>
        <div style="color:#FFB100; font-size:16px; font-weight:bold;">{dom_str}</div>
    </div>""", unsafe_allow_html=True)
with gh_cols[2]:
    st.markdown(f"""<div class="mover-box">
        <div style="color:#888; font-size:10px;">TOTAL MARKET CAP</div>
        <div style="color:#E0E0E0; font-size:16px; font-weight:bold;">{total_mcap}</div>
    </div>""", unsafe_allow_html=True)
with gh_cols[3]:
    now_str = time.strftime("%H:%M:%S UTC", time.gmtime())
    st.markdown(f"""<div class="mover-box">
        <div style="color:#888; font-size:10px;">SYSTEM TIME</div>
        <div style="color:#E0E0E0; font-size:16px; font-weight:bold;">{now_str}</div>
    </div>""", unsafe_allow_html=True)

# =====================================================================
# SECTION 3 — SIDEBAR
# =====================================================================
with st.sidebar:
    st.title("Antigravity")
    st.markdown("---")

    market_type = st.selectbox("Market Mode", ["Crypto", "Stocks", "Forex"])
    if market_type == "Crypto":   ticker_list = CRYPTO_100
    elif market_type == "Stocks": ticker_list = STOCKS_100
    else:                          ticker_list = FOREX_20

    display_ticker = st.selectbox("Asset Ticker", ticker_list)
    active_ticker  = (display_ticker.replace('/', '') + '=X'
                      if market_type == "Forex" else display_ticker)

    # SMC Toggles
    st.markdown("### SMC Overlays")
    show_fvg    = st.checkbox("Show FVG",           value=True)
    show_bos    = st.checkbox("Show BOS",           value=True)
    show_choch  = st.checkbox("Show CHoCH",         value=False)
    show_ob     = st.checkbox("Show Order Blocks",  value=False)
    show_volume = st.checkbox("Show Volume Profile", value=True)

    # Pre-fetch for Bias
    intel_data  = fetch_intel_cached(active_ticker, market_type)
    social_data = fetch_social_cached(active_ticker, market_type)
    oscore  = intel_data.get('outlook_score', 0)
    s_spike = social_data.get('spike', False)

    if intel_data.get('news'): sys_logs.append("[SUCCESS] INTEL_FETCHED")
    else:                       sys_logs.append("[WARNING] INTEL_TIMEOUT")
    if social_data.get('dominance', 0) > 0: sys_logs.append("[SUCCESS] SOCIAL_LIVE")

    # Terminal Bias
    if   oscore ==  1 and s_spike: master_bias = "HIGH CONVICTION BULLISH"; mb_color = "#00D1FF"
    elif oscore == -1 and s_spike: master_bias = "HIGH CONVICTION BEARISH"; mb_color = "#FF4B4B"
    elif oscore ==  1:             master_bias = "BULLISH TREND";            mb_color = "#00D1FF"
    elif oscore == -1:             master_bias = "BEARISH TREND";            mb_color = "#FF4B4B"
    elif s_spike:                  master_bias = "DIVERGENT - CAUTION";     mb_color = "#FFB100"
    else:                          master_bias = "NEUTRAL";                  mb_color = "#888888"

    st.markdown(f"""
    <div style='border:1px dashed {mb_color}; padding:10px; text-align:center; margin:10px 0 20px 0;'>
        <span style='color:#888; font-size:11px;'>&gt;&gt;&gt; TERMINAL_BIAS &lt;&lt;&lt;</span><br/>
        <span style='color:{mb_color}; font-weight:bold; font-size:16px;'>{master_bias}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Controls")
    auto_refresh = st.checkbox("Enable Auto-Refresh", value=False)
    refresh_rate = st.slider("Refresh Interval (s)", 5, 60, 15)
    if st.button("Force Clear Cache & Refresh"):
        st.cache_data.clear()
        st.rerun()

# =====================================================================
# SECTION 4 — MARKET MOVERS (Toggle by Market)
# =====================================================================
st.markdown("---")
mover_col, toggle_col = st.columns([5, 1])
with toggle_col:
    mover_market = st.radio("Movers", ["Crypto", "Stocks", "FX"],
                            horizontal=False, label_visibility="collapsed",
                            index=["Crypto", "Stocks", "FX"].index(
                                "Crypto" if market_type == "Crypto"
                                else "Stocks" if market_type == "Stocks" else "FX"))

movers_mt = "Crypto" if mover_market == "Crypto" else "Stocks" if mover_market == "Stocks" else "Forex"
movers = fetch_movers_cached(movers_mt)

with mover_col:
    if movers and (movers['gainers'] or movers['losers']):
        sys_logs.append("[SUCCESS] MOVERS_FETCHED")
        # Gainers row
        st.markdown(f"<span style='color:#00D1FF; font-size:11px; font-family:monospace;'>▲ TOP GAINERS — {mover_market}</span>", unsafe_allow_html=True)
        g_cols = st.columns(7)
        for i, g in enumerate(movers['gainers'][:7]):
            chg = g['change']; c = "#00D1FF" if chg >= 0 else "#FF4B4B"; sgn = "+" if chg >= 0 else ""
            with g_cols[i]:
                st.markdown(f"""<div class="mover-box">
                    <div class="sym">{g['symbol']}</div>
                    <div class="price">{g['price']}</div>
                    <div style="color:{c};">{sgn}{chg:.2f}%</div>
                </div>""", unsafe_allow_html=True)
        # Losers row
        st.markdown(f"<span style='color:#FF4B4B; font-size:11px; font-family:monospace;'>▼ TOP LOSERS — {mover_market}</span>", unsafe_allow_html=True)
        l_cols = st.columns(7)
        for i, l in enumerate(movers['losers'][:7]):
            chg = l['change']; c = "#00D1FF" if chg >= 0 else "#FF4B4B"; sgn = "+" if chg >= 0 else ""
            with l_cols[i]:
                st.markdown(f"""<div class="mover-box">
                    <div class="sym">{l['symbol']}</div>
                    <div class="price">{l['price']}</div>
                    <div style="color:{c};">{sgn}{chg:.2f}%</div>
                </div>""", unsafe_allow_html=True)
    else:
        sys_logs.append("[WARNING] MOVERS_TIMEOUT")
        st.markdown("<span style='color:#555; font-size:11px;'>[!] Movers data unavailable</span>", unsafe_allow_html=True)

# =====================================================================
# SECTION 5 — TIMEFRAME ROW
# =====================================================================
st.markdown(f"## {display_ticker} | {market_type.upper()} MODULE")

TIMEFRAMES = ['1h', '4h', '8h', '12h', '1D', '3D', '1W', '1M']
if 'active_tf' not in st.session_state:
    st.session_state.active_tf = '1h'

tf_cols = st.columns(len(TIMEFRAMES))
for i, tf in enumerate(TIMEFRAMES):
    with tf_cols[i]:
        active_style = "background-color:#00D1FF; color:#0E1117;" if st.session_state.active_tf == tf else ""
        if st.button(tf, key=f"tf_{tf}", use_container_width=True):
            st.session_state.active_tf = tf
            st.rerun()

active_tf = st.session_state.active_tf

# =====================================================================
# SECTION 6 — MAIN LAYOUT [6 : 1]
# =====================================================================
col_main, col_intel = st.columns([6, 1])

with col_main:
    df = fetch_candles_cached(active_ticker, active_tf, limit=150)

    if not df.empty and 'close' in df.columns:
        sys_logs.append("[SUCCESS] DATA_FETCHED")
        structures = smc.detect_structures(df)

        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'],
            increasing_line_color='#00D1FF', increasing_fillcolor='#00D1FF',
            decreasing_line_color='#FF4B4B',  decreasing_fillcolor='#FF4B4B',
            name='Price'
        )])

        if show_fvg:
            for fvg in structures['fvgs']:
                fc = 'rgba(0,209,255,0.15)' if fvg['type'] == 'bullish' else 'rgba(255,75,75,0.15)'
                fig.add_shape(type="rect", x0=fvg['start_time'], y0=fvg['bottom'],
                              x1=fvg['end_time'], y1=fvg['top'],
                              fillcolor=fc, line=dict(width=0), layer="below")

        if show_bos:
            for bos in structures['bos']:
                bc = '#00D1FF' if bos['type'] == 'bullish' else '#FF4B4B'
                fig.add_shape(type="line", x0=bos['start_time'], y0=bos['price'],
                              x1=bos['end_time'], y1=bos['price'],
                              line=dict(color=bc, width=1.5, dash="dash"), layer="above")

        # CHoCH — annotate first BOS of opposite direction as CHoCH
        if show_choch and structures['bos']:
            prev_type = None
            for bos in structures['bos']:
                if prev_type and bos['type'] != prev_type:
                    cc = '#00D1FF' if bos['type'] == 'bullish' else '#FF4B4B'
                    fig.add_annotation(x=bos['end_time'], y=bos['price'],
                                       text="CHoCH", showarrow=False,
                                       font=dict(color=cc, size=10, family="Courier New"),
                                       bgcolor="#1A1C23", bordercolor=cc, borderwidth=1)
                prev_type = bos['type']

        # Order Blocks — highlight last bullish/bearish candle before a BOS
        if show_ob and len(df) > 5:
            for bos in structures['bos'][-5:]:
                idx = df.index.get_indexer([bos['start_time']], method='nearest')[0]
                if idx > 0:
                    ob_candle = df.iloc[idx - 1]
                    ob_c = 'rgba(0,209,255,0.25)' if bos['type'] == 'bullish' else 'rgba(255,75,75,0.25)'
                    fig.add_shape(type="rect",
                                  x0=df.index[idx-1], y0=ob_candle['low'],
                                  x1=df.index[idx],   y1=ob_candle['high'],
                                  fillcolor=ob_c, line=dict(width=1, color=ob_c), layer="below")

        # Volume Profile (Visible Range) — amber bars on right 16% of chart
        if show_volume and 'volume' in df.columns:
            price_min = float(df['low'].min())
            price_max = float(df['high'].max())
            num_bins  = 30
            bin_size  = (price_max - price_min) / num_bins if price_max > price_min else 1
            vp_bins   = {}
            for _, row in df.iterrows():
                b = int((float(row['close']) - price_min) / bin_size)
                b = max(0, min(b, num_bins - 1))
                vp_bins[b] = vp_bins.get(b, 0) + float(row['volume'])
            if vp_bins:
                max_vol = max(vp_bins.values())
                x_start = df.index[int(len(df) * 0.84)]
                x_end   = df.index[-1]
                for b, vol in vp_bins.items():
                    y_lo  = price_min + b * bin_size
                    y_hi  = y_lo + bin_size
                    alpha = 0.05 + 0.3 * (vol / max_vol)
                    vc    = f'rgba(255,177,0,{alpha:.2f})'
                    fig.add_shape(type='rect', x0=x_start, x1=x_end,
                                  y0=y_lo, y1=y_hi,
                                  fillcolor=vc, line=dict(width=0), layer='below')

        # Watermark HUD
        fig.add_annotation(
            text=f"{active_ticker} | {active_tf}",
            xref="paper", yref="paper",
            x=0.03, y=0.97,
            showarrow=False,
            font=dict(family="Courier New, monospace", size=50, color="rgba(0, 209, 255, 0.15)"),
            align="left", xanchor="left", yanchor="top"
        )

        fig.update_layout(
            template='plotly_dark', paper_bgcolor='#0E1117', plot_bgcolor='#0E1117',
            xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0),
            font=dict(family="Courier New, monospace", color="#E0E0E0"), height=520,
            hovermode='x unified',
            xaxis=dict(
                showgrid=False, zeroline=False,
                spikemode='across', spikesnap='cursor',
                spikecolor='#555', spikethickness=1, spikedash='dot',
            ),
            yaxis=dict(
                showgrid=True, gridcolor='#1F1F1F', zeroline=False,
                autorange=True, fixedrange=False, automargin=True,
                spikemode='across', spikesnap='cursor',
                spikecolor='#555', spikethickness=1, spikedash='dot',
                tickformat='.4f' if float(df['close'].iloc[-1]) < 1 else '.2f',
            )
        )

        st.markdown("<div class='chart-panel'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        sys_logs.append("[ERROR] SOURCE_TIMEOUT")
        st.markdown(f"<div style='border:1px solid #FF4B4B; padding:20px; color:#FF4B4B; "
                    f"font-family:monospace;'>[!] TICKER_NOT_FOUND: {display_ticker}</div>",
                    unsafe_allow_html=True)

with col_intel:
    st.markdown("<div class='intel-panel'>", unsafe_allow_html=True)
    st.markdown("### WIRE")

    pct = intel_data.get('pct', 0)
    gc  = "#00D1FF" if oscore == 1 else "#FF4B4B" if oscore == -1 else "#888"
    st.markdown(f"""
    <div style='border:1px solid #333; padding:8px; text-align:center; margin-bottom:10px;'>
        <span style='color:#888; font-size:11px;'>OUTLOOK</span><br/>
        <span style='color:{gc}; font-size:18px; font-weight:bold;'>{intel_data.get('outlook','0% NEUTRAL')}</span>
        <div style="width:100%; background:#1A1C23; border:1px solid #333; height:6px; margin-top:6px;">
          <div style="width:{pct}%; background:{gc}; height:100%;"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    if intel_data['news']:
        for n in intel_data['news'][:14]:
            if n['score'] == 1:  tc = "#00D1FF"; tag = "[BULL]"
            elif n['score'] == -1: tc = "#FF4B4B"; tag = "[BEAR]"
            else:                 tc = "#888";    tag = "[NEUT]"
            ta = n.get('time_ago', '')
            st.markdown(f"""<div style="margin-bottom:8px; font-size:10px; font-family:monospace;">
                <span style="color:{tc}; font-weight:bold;">{tag}</span>
                <span style="color:#444;"> {n.get('source','')}</span>
                <span style="color:#444; float:right;">{ta}</span><br/>
                <a href="{n['link']}" target="_blank"
                   style="color:#C0C0C0; text-decoration:none;">{n['title'][:75]}</a>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#888; font-size:11px;'>[NEUT] No wire data.</span>",
                    unsafe_allow_html=True)

    st.markdown("---")
    if social_data.get('spike', False):
        st.markdown("<div style='background:#332200; border:1px solid #FFB100; color:#FFB100; "
                    "padding:6px; text-align:center; font-size:10px; font-weight:bold; "
                    "margin-bottom:8px;'>[!] SPIKE</div>", unsafe_allow_html=True)
        sys_logs.append("[WARNING] SOCIAL_SPIKE")
    st.markdown(f"<div style='font-size:11px;'>Dominance: "
                f"<span style='color:#00D1FF;'>{social_data.get('dominance',0):.1f}%</span></div>",
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# SECTION 6b — DERIVATIVES HEALTH STRIP
# =====================================================================
if market_type == "Crypto":
    deriv = fetch_derivatives_cached(active_ticker)
    sys_logs.append("[SUCCESS] DERIV_LIVE" if deriv.get('funding_rate') is not None else "[WARNING] DERIV_TIMEOUT")

    oi_val  = deriv.get('oi')
    oi_chg  = deriv.get('oi_change_24h')
    fr_val  = deriv.get('funding_rate')
    gh_data = fetch_global_health_cached()
    btc_dom = gh_data.get('btc_dominance')

    oi_str     = f"{oi_val:,.0f}" if oi_val else "N/A"
    oi_chg_str = (f"+{oi_chg:.2f}%" if (oi_chg or 0) >= 0 else f"{oi_chg:.2f}%") if oi_chg is not None else "N/A"
    oi_chg_col = "#00D1FF" if (oi_chg or 0) >= 0 else "#FF4B4B"

    if fr_val is not None:
        fr_color = "#FF4B4B" if fr_val >= 0 else "#00D1FF"
        fr_str   = f"{'+' if fr_val >= 0 else ''}{fr_val:.4f}%"
        fr_label = "LONGS PAYING" if fr_val >= 0 else "SHORTS PAYING"
    else:
        fr_color = "#888"; fr_str = "N/A"; fr_label = ""

    dom_str   = f"{btc_dom:.1f}%" if btc_dom else "N/A"
    fng_val   = gh_data.get('fng_value')
    fng_lbl   = gh_data.get('fng_label', 'N/A')
    fng_color = "#00D1FF" if (fng_val or 0) >= 55 else "#FF4B4B" if (fng_val or 100) <= 44 else "#888"
    fng_str   = f"{fng_val} — {fng_lbl}" if fng_val else "N/A"

    d_cols = st.columns(4)
    with d_cols[0]:
        st.markdown(f"""<div class="mover-box">
            <div style="color:#888; font-size:10px;">OPEN INTEREST</div>
            <div style="color:#E0E0E0; font-size:15px; font-weight:bold;">{oi_str}</div>
            <div style="color:{oi_chg_col}; font-size:12px;">24h: {oi_chg_str}</div>
        </div>""", unsafe_allow_html=True)
    with d_cols[1]:
        st.markdown(f"""<div class="mover-box">
            <div style="color:#888; font-size:10px;">FUNDING RATE</div>
            <div style="color:{fr_color}; font-size:15px; font-weight:bold;">{fr_str}</div>
            <div style="color:{fr_color}; font-size:10px;">{fr_label}</div>
        </div>""", unsafe_allow_html=True)
    with d_cols[2]:
        st.markdown(f"""<div class="mover-box">
            <div style="color:#888; font-size:10px;">BTC DOMINANCE</div>
            <div style="color:#FFB100; font-size:15px; font-weight:bold;">{dom_str}</div>
        </div>""", unsafe_allow_html=True)
    with d_cols[3]:
        st.markdown(f"""<div class="mover-box">
            <div style="color:#888; font-size:10px;">FEAR & GREED</div>
            <div style="color:{fng_color}; font-size:15px; font-weight:bold;">{fng_str}</div>
        </div>""", unsafe_allow_html=True)

# =====================================================================
# SECTION 7 — NEWS CHANNELS (sorted by timestamp)
# =====================================================================
st.markdown("---")
st.markdown("### NEWS CHANNELS")

def _ta_to_seconds(ta):
    """Convert '5m ago' / '2h ago' / '1d ago' -> seconds for sorting."""
    if not ta: return 999999
    try:
        val = int(''.join(filter(str.isdigit, ta)))
        if 'm' in ta: return val * 60
        if 'h' in ta: return val * 3600
        if 'd' in ta: return val * 86400
        if 's' in ta: return val
    except: pass
    return 999999

all_news  = sorted(intel_data.get('news', []), key=lambda n: _ta_to_seconds(n.get('time_ago', '')))
bull_news = [n for n in all_news if n['score'] ==  1]
neut_news = [n for n in all_news if n['score'] ==  0]
bear_news = [n for n in all_news if n['score'] == -1]

def render_news_item(n):
    ta    = n.get('time_ago', '')
    src   = n.get('source', '')
    link  = n.get('link', '#')
    title = n.get('title', '')[:95]
    return (
        f"<div style='margin-bottom:8px; font-size:11px; border-bottom:1px solid #222; padding-bottom:6px;'>"
        f"<span style='color:#555;'>{src} </span>"
        f"<span style='color:#444; font-size:10px;'>{ta}</span><br/>"
        f"<a href='{link}' target='_blank' style='color:#E0E0E0; text-decoration:none;'>{title}</a>"
        f"</div>"
    )

ch_bull, ch_neut, ch_bear = st.columns(3)

with ch_bull:
    items = "".join(render_news_item(n) for n in bull_news[:6]) or "<span style='color:#444;'>--- EMPTY ---</span>"
    st.markdown(f"""<div class="news-channel">
        <div class="ch-header" style="color:#00D1FF;">▲ BULLISH_WIRE ({len(bull_news)})</div>
        {items}</div>""", unsafe_allow_html=True)

with ch_neut:
    items = "".join(render_news_item(n) for n in neut_news[:6]) or "<span style='color:#444;'>--- EMPTY ---</span>"
    st.markdown(f"""<div class="news-channel">
        <div class="ch-header" style="color:#888;">— NEUTRAL_WIRE ({len(neut_news)})</div>
        {items}</div>""", unsafe_allow_html=True)

with ch_bear:
    items = "".join(render_news_item(n) for n in bear_news[:6]) or "<span style='color:#444;'>--- EMPTY ---</span>"
    st.markdown(f"""<div class="news-channel">
        <div class="ch-header" style="color:#FF4B4B;">▼ BEARISH_WIRE ({len(bear_news)})</div>
        {items}</div>""", unsafe_allow_html=True)

# =====================================================================
# SECTION 8 — SYSTEM LOG (Sidebar bottom)
# =====================================================================
with st.sidebar:
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("### SYSTEM LOG")
    log_html = ""
    for log in sys_logs:
        c = "#00D1FF" if "SUCCESS" in log else "#FF4B4B" if "ERROR" in log else "#FFB100"
        log_html += f"<span style='color:{c};'>{log}</span><br/>"
    st.markdown(f"<div style='border:1px solid #333; padding:8px; font-size:10px; "
                f"font-family:monospace; background:#0E1117;'>{log_html}</div>",
                unsafe_allow_html=True)

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
