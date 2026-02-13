import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BNPL Under the Microscope",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme Colors ──────────────────────────────────────────────────────────────
GOLD    = "#E8C56D"
RED     = "#FF5B5B"
GREEN   = "#6FCF97"
BLUE    = "#4A9EFF"
ORANGE  = "#C45C3A"
MUTED   = "#7A7A8A"
BG      = "#0A0A0C"
SURFACE = "#111116"

TICKER_COLORS = {
    "KLAR":  GOLD,
    "AFRM":  GREEN,
    "PYPL":  BLUE,
    "SQ":    ORANGE,
    "^GSPC": MUTED,
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor=BG,
        plot_bgcolor=SURFACE,
        font=dict(family="monospace", color=MUTED, size=11),
        xaxis=dict(gridcolor="#1E1E28", linecolor="#2A2A35"),
        yaxis=dict(gridcolor="#1E1E28", linecolor="#2A2A35"),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="#2A2A35"),
        margin=dict(t=40, b=40, l=40, r=40),
    )
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:wght@700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #0a0a0c;
    color: #e8e6e0;
}

.main { background-color: #0a0a0c; }
.block-container { padding-top: 2rem; max-width: 1400px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111116;
    border-right: 1px solid #2a2a35;
}
[data-testid="stSidebar"] * { color: #e8e6e0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #111116;
    border: 1px solid #2a2a35;
    border-radius: 4px;
    padding: 16px;
}
[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace !important; font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.7rem !important; letter-spacing: 2px; text-transform: uppercase; color: #7a7a8a !important; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* Headers */
h1 { font-family: 'Playfair Display', serif !important; font-size: 2.8rem !important; color: white !important; }
h2 { font-family: 'IBM Plex Mono', monospace !important; font-size: 1rem !important;
     letter-spacing: 3px; text-transform: uppercase; color: #E8C56D !important; border-bottom: 1px solid #2a2a35; padding-bottom: 8px; }
h3 { font-family: 'IBM Plex Mono', monospace !important; color: #e8e6e0 !important; }

/* Tabs */
[data-testid="stTab"] { font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; }
button[data-baseweb="tab"] { background: transparent !important; color: #7a7a8a !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #E8C56D !important; border-bottom: 2px solid #E8C56D !important; }

/* Selectbox / inputs */
[data-testid="stSelectbox"] > div > div { background: #111116 !important; border-color: #2a2a35 !important; }

/* Info boxes */
.insight-box {
    background: rgba(232,197,109,0.06);
    border-left: 3px solid #E8C56D;
    padding: 14px 18px;
    border-radius: 0 4px 4px 0;
    margin: 12px 0;
    font-size: 13px;
    line-height: 1.7;
}
.insight-box.danger {
    background: rgba(255,91,91,0.06);
    border-left-color: #FF5B5B;
}
.insight-box.green {
    background: rgba(111,207,151,0.06);
    border-left-color: #6FCF97;
}
.insight-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #E8C56D;
    margin-bottom: 6px;
    display: block;
}
.hero-sub { color: #7a7a8a; font-size: 15px; max-width: 700px; line-height: 1.7; margin-bottom: 32px; }
.divider { height: 1px; background: linear-gradient(90deg, #E8C56D, transparent); opacity: 0.3; margin: 24px 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner="Fetching live market data...")
def load_stock_data():
    tickers = ["KLAR", "AFRM", "PYPL", "SQ", "^GSPC"]
    try:
        raw = yf.download(tickers, start="2025-09-10", auto_adjust=True, progress=False)
        prices = raw["Close"].copy()
        prices.columns.name = None
        prices_norm = prices.div(prices.iloc[0]) * 100
        returns = prices.pct_change().dropna()
        return prices, prices_norm, returns
    except Exception:
        return None, None, None


def get_static_data():
    """All fundamental + risk data hardcoded from public sources."""

    klarna_annual = pd.DataFrame({
        "year":             [2019, 2020, 2021, 2022, 2023, 2024, 2025],
        "revenue_m":        [602,  845,  1204, 1850, 2277, 2810, 3500],
        "net_income_m":     [-93,  -153, -688, -1047,-241,  55,  -200],
        "gmv_b":            [35,   53,   80,   100,  90,   105,  130],
        "active_users_m":   [70,   87,   90,   97,   100,  108,  114],
        "merchants_k":      [190,  250,  400,  500,  550,  616,  850],
        "headcount":        [3500, 4000, 6500, 7000, 5200, 4300, 3800],
    })
    klarna_annual["revenue_growth"] = klarna_annual["revenue_m"].pct_change() * 100
    klarna_annual["arpu"] = klarna_annual["revenue_m"] / klarna_annual["active_users_m"]
    klarna_annual["take_rate"] = klarna_annual["revenue_m"] / (klarna_annual["gmv_b"] * 1000) * 100

    klarna_qtr = pd.DataFrame({
        "quarter":       ["Q1 2024","Q2 2024","Q3 2024","Q4 2024","Q1 2025","Q2 2025","Q3 2025"],
        "revenue_m":     [614, 706, 706, 784, 701, 823, 903],
        "net_income_m":  [8,   12,  12,  30,  -60, -57, -95],
        "gmv_b":         [22.0,24.5,26.2,31.0,27.0,29.5,32.7],
        "users_m":       [100, 102, 105, 108, 109, 111, 114],
        "merchants_k":   [500, 550, 616, 680, 720, 800, 850],
    })

    valuation = pd.DataFrame({
        "event":        ["Series D","Series E","Peak","Down-round","Private","Pre-IPO","IPO Day 1","ATH","Current"],
        "date":         ["Feb 2019","Sep 2020","Jun 2021","Jul 2022","Jul 2023","Jun 2024","Sep 10 2025","Dec 4 2025","Feb 11 2026"],
        "valuation_b":  [5.5, 10.6, 45.6, 6.7, 9.0, 14.0, 17.0, 19.7, 7.82],
        "price":        [None,None,None,None,None,None,45.82,57.20,19.75],
    })

    delinquency = pd.DataFrame({
        "type":   ["BNPL official default","BNPL self-reported late","Overall consumer debt","Credit cards","Auto loans","Student loans 90+","Klarna charge-off"],
        "rate":   [1.83, 41.0, 3.5, 8.8, 4.2, 7.7, 0.54],
        "source": ["CFPB Dec 2025","LendingTree 2025","NY Fed Q1 2025","NY Fed Q1 2025","NY Fed Q1 2025","NY Fed Q1 2025","Klarna Q2 2025"],
    })

    late_pay = pd.DataFrame({
        "demographic":  ["Gen Z (18-26)","Millennials (27-42)","Gen X (43-58)","Boomers (59+)"],
        "rate_2024":    [44, 34, 8, 4],
        "rate_2025":    [51, 38, 10, 5],
    })

    market_size = pd.DataFrame({
        "year":        [2019,2020,2021,2022,2023,2024,2025,2026,2027,2028],
        "global_b":    [35,  90, 186, 310, 420, 492, 560, 625, 695, 770],
        "us_b":        [6,   20,  38,  60,  82, 103, 116.7,130,145,163.8],
        "projected":   [False]*6 + [True]*4,
    })

    competitors = pd.DataFrame({
        "company":      ["Klarna","Affirm","PayPal","Block/Afterpay"],
        "ticker":       ["KLAR","AFRM","PYPL","SQ"],
        "users_m":      [114, 21, 400, 20],
        "rev_growth":   [26, 36, 5, 8],
        "mktcap_b":     [7.82, 15.0, 72.0, 38.0],
        "ps_ratio":     [2.24, 5.66, 2.32, 1.73],
        "profitable":   [False, False, True, False],
        "ret_since_ipo":[-51, 12, -18, -8],
    })

    return klarna_annual, klarna_qtr, valuation, delinquency, late_pay, market_size, competitors


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 📊 BNPL MICROSCOPE")
    st.markdown("<div style='color:#7a7a8a;font-size:11px;letter-spacing:1px;'>Data Analysis Project · Feb 2026</div>", unsafe_allow_html=True)
    st.markdown("---")

    section = st.radio("Navigation", [
        "🏠 Overview",
        "📈 Klarna Stock",
        "💰 Fundamentals",
        "⚠️  Debt Risk",
        "🏆 Competitors",
        "📋 Verdict",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Live Data**")
    refresh = st.button("🔄 Refresh Market Data")
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px;color:#7a7a8a;line-height:1.8;'>
    <b>Sources</b><br>
    Klarna SEC F-1 Filing<br>
    CFPB BNPL Reports 2025<br>
    NY Fed Credit Panel Q1 2025<br>
    Morgan Stanley AlphaWise<br>
    LendingTree Survey 2025<br>
    Richmond Fed EB-25-03<br>
    Yahoo Finance (live)<br><br>
    <i>Not financial advice.</i>
    </div>
    """, unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
prices, prices_norm, returns = load_stock_data()
kl_annual, kl_qtr, valuation, delinquency, late_pay, market_size, competitors = get_static_data()

live_data_ok = prices is not None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if section == "🏠 Overview":
    st.markdown("# BNPL *Under the* Microscope")
    st.markdown('<p class="hero-sub">Klarna\'s IPO collapse, the Buy Now Pay Later debt trap, and what $560B in consumer credit tells us about the future of fintech.</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("KLAR Current", "$19.75", "-65% from ATH", delta_color="inverse")
    with c2:
        st.metric("IPO Price", "$40.00", "+15% day one")
    with c3:
        st.metric("52-Week High", "$57.20", "Dec 4 2025")
    with c4:
        st.metric("Analyst Target", "$43.29", "+119% upside")
    with c5:
        st.metric("Late Payments", "41%", "+7pp YoY", delta_color="inverse")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("## Valuation Timeline")
        fig = go.Figure()
        bar_colors = [
            MUTED, MUTED, GOLD, RED, MUTED, MUTED, GREEN, GOLD, RED
        ]
        fig.add_trace(go.Bar(
            x=valuation["event"],
            y=valuation["valuation_b"],
            marker_color=bar_colors,
            text=[f"${v}B" for v in valuation["valuation_b"]],
            textposition="outside",
            textfont=dict(color="white", size=10),
        ))
        fig.update_layout(
            **PLOTLY_TEMPLATE["layout"],
            height=340,
            yaxis_title="Valuation (USD Billions)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("## Key Events")
        events = [
            (GOLD,  "Jun 2021",     "Peak: $45.6B",            "Europe's most valuable startup. Zero-rate era."),
            (RED,   "Jul 2022",     "Crash: $6.7B",            "−85% in 13 months. Rate hikes crushed multiples."),
            (GREEN, "Sep 10 2025",  "IPO: $40/sh → $45.82",   "Largest fintech IPO of 2025. +15% day one."),
            (GOLD,  "Dec 4 2025",   "ATH: $57.20",             "Peak post-IPO enthusiasm."),
            (RED,   "Nov 18 2025",  "Q3 miss sentiment",       "Beat revenue, but net loss −$95M. Stock −9%."),
            (RED,   "Jan–Feb 2026", "Class Actions Filed",     "Multiple law firms file securities fraud suits."),
        ]
        for color, date, title, body in events:
            st.markdown(f"""
            <div style='display:flex;gap:12px;margin-bottom:14px;align-items:flex-start;'>
                <div style='width:8px;height:8px;border-radius:50%;background:{color};margin-top:6px;flex-shrink:0;'></div>
                <div>
                    <div style='font-size:10px;color:{color};letter-spacing:1px;'>{date}</div>
                    <div style='font-size:13px;font-weight:bold;color:white;'>{title}</div>
                    <div style='font-size:12px;color:#7a7a8a;'>{body}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION: KLARNA STOCK
# ══════════════════════════════════════════════════════════════════════════════

elif section == "📈 Klarna Stock":
    st.markdown("## § 01 — Stock Performance")

    if not live_data_ok:
        st.warning("Live data unavailable. Check internet connection or refresh.")
    else:
        # Safe extraction — KLAR may have fewer rows than other tickers
        klar = prices["KLAR"].dropna() if "KLAR" in prices.columns else pd.Series(dtype=float)
        ret  = returns["KLAR"].dropna() if "KLAR" in returns.columns else pd.Series(dtype=float)

        if len(klar) == 0:
            st.warning("KLAR price data not yet available from yfinance. Try refreshing.")
            st.stop()

        current_price = float(klar.iloc[-1])
        today_ret     = float(ret.iloc[-1]) * 100 if len(ret) > 0 else 0.0
        ann_vol       = float(ret.std() * np.sqrt(252) * 100) if len(ret) > 1 else 0.0

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Current Price", f"${current_price:.2f}", f"{today_ret:+.2f}% today")
        with c2: st.metric("From IPO ($40)", f"{(current_price/40-1)*100:.1f}%", delta_color="inverse")
        with c3: st.metric("From ATH ($57.20)", f"{(current_price/57.20-1)*100:.1f}%", delta_color="inverse")
        with c4: st.metric("Ann. Volatility", f"{ann_vol:.1f}%", "vs S&P ~15%")

        st.markdown("---")

        # Tabs
        t1, t2, t3 = st.tabs(["📊  KLAR Price Chart", "📉  Relative Performance", "🎲  Risk Analysis"])

        with t1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=prices.index, y=prices["KLAR"],
                fill="tozeroy",
                fillcolor="rgba(232,197,109,0.07)",
                line=dict(color=GOLD, width=2),
                name="KLAR",
                hovertemplate="<b>%{x|%b %d}</b><br>$%{y:.2f}<extra></extra>",
            ))
            # Key level lines
            fig.add_hline(y=40, line_dash="dash", line_color=MUTED, annotation_text="IPO Price $40", annotation_font_size=10)
            fig.add_hline(y=57.20, line_dash="dot", line_color=GOLD, annotation_text="ATH $57.20", annotation_font_size=10)
            fig.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                height=400, yaxis_title="Price (USD)",
                title=dict(text="Klarna (KLAR) — Post-IPO Price History", font=dict(color="white", size=13)),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="insight-box danger">
            <span class="insight-label">Key Observation</span>
            KLAR peaked at $57.20 on Dec 4, 2025 — just 12 weeks after IPO — and has since fallen
            65% to $19.75. The drop was driven by Q3 net loss of −$95M, class-action lawsuits filed
            in Jan–Feb 2026, and broader fintech multiple compression. Q4 2025 earnings (Feb 25) are
            the next major catalyst.
            </div>
            """, unsafe_allow_html=True)

        with t2:
            fig = go.Figure()
            labels = {"KLAR": "Klarna", "AFRM": "Affirm", "PYPL": "PayPal", "SQ": "Block", "^GSPC": "S&P 500"}
            widths = {"KLAR": 2.5, "AFRM": 1.8, "PYPL": 1.8, "SQ": 1.8, "^GSPC": 1.5}
            dashes = {"KLAR": "solid", "AFRM": "dash", "PYPL": "dash", "SQ": "dash", "^GSPC": "dot"}

            for ticker in ["KLAR", "AFRM", "PYPL", "SQ", "^GSPC"]:
                fig.add_trace(go.Scatter(
                    x=prices_norm.index,
                    y=prices_norm[ticker],
                    name=labels[ticker],
                    line=dict(color=TICKER_COLORS[ticker], width=widths[ticker], dash=dashes[ticker]),
                    hovertemplate=f"<b>{labels[ticker]}</b><br>%{{x|%b %d}}<br>Indexed: %{{y:.1f}}<extra></extra>",
                ))
            fig.add_hline(y=100, line_color="#2A2A35", line_dash="dot",
                         annotation_text="IPO baseline", annotation_font_size=9)
            fig.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                height=420, yaxis_title="Indexed Price (100 = Sep 10 2025)",
                title=dict(text="Relative Performance Since Klarna IPO (Sep 10, 2025 = 100)", font=dict(color="white", size=13)),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div class="insight-box">
            <span class="insight-label">Analyst Insight</span>
            Affirm (+12%) has significantly outperformed Klarna (−51%) despite operating in the same
            sector with the same macro backdrop. Affirm's focus on fewer, larger merchants (Amazon,
            Walmart) with interest-bearing loans produces cleaner, more predictable revenue —
            which the market rewards.
            </div>
            """, unsafe_allow_html=True)

        with t3:
            col1, col2 = st.columns(2)

            with col1:
                # Returns distribution
                if "KLAR" not in returns.columns or len(returns["KLAR"].dropna()) == 0:
                    st.info("KLAR return data not yet available.")
                else:
                    klar_ret = returns["KLAR"].dropna() * 100
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=klar_ret, nbinsx=40,
                        marker_color=GOLD, opacity=0.7, name="Daily Returns",
                    ))
                    fig.add_vline(x=float(klar_ret.mean()), line_color=RED, line_dash="dash",
                                 annotation_text=f"Mean: {klar_ret.mean():.2f}%", annotation_font_size=10)
                    fig.add_vline(x=0, line_color=MUTED, line_dash="dot")
                    fig.update_layout(
                        **PLOTLY_TEMPLATE["layout"],
                        height=320, xaxis_title="Daily Return (%)",
                        title=dict(text="KLAR Daily Returns Distribution", font=dict(color="white", size=12)),
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Risk/return scatter — fully dynamic, no hardcoded lengths
                TICKER_LABEL_MAP = {
                    "KLAR": "Klarna", "AFRM": "Affirm",
                    "PYPL": "PayPal", "SQ": "Block", "^GSPC": "S&P 500"
                }
                ALL_COLORS = {**TICKER_COLORS, "^GSPC": MUTED}

                avail = [t for t in ["KLAR","AFRM","PYPL","SQ","^GSPC"]
                         if t in returns.columns]
                rows = []
                for t in avail:
                    r = returns[t].dropna()
                    if len(r) > 1:
                        rows.append({
                            "ticker":     t,
                            "ann_return": r.mean() * 252 * 100,
                            "ann_vol":    r.std()  * np.sqrt(252) * 100,
                            "label":      TICKER_LABEL_MAP.get(t, t),
                            "color":      ALL_COLORS.get(t, MUTED),
                        })

                if rows:
                    s = pd.DataFrame(rows)
                    fig = go.Figure()
                    for _, row in s.iterrows():
                        fig.add_trace(go.Scatter(
                            x=[row["ann_vol"]], y=[row["ann_return"]],
                            mode="markers+text",
                            marker=dict(size=14, color=row["color"]),
                            text=[row["label"]],
                            textposition="top right",
                            textfont=dict(color=row["color"], size=10),
                            showlegend=False,
                        ))
                    fig.add_hline(y=0, line_color="#2A2A35", line_dash="dot")
                    fig.update_layout(
                        **PLOTLY_TEMPLATE["layout"],
                        height=320,
                        xaxis_title="Annualised Volatility (%)",
                        yaxis_title="Annualised Return (%)",
                        title=dict(text="Risk vs Return (Annualised, Since IPO)",
                                   font=dict(color="white", size=12)),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data yet for risk/return scatter.")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION: FUNDAMENTALS
# ══════════════════════════════════════════════════════════════════════════════

elif section == "💰 Fundamentals":
    st.markdown("## § 02 — Revenue & Fundamentals")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Q3 2025 Revenue", "$903M", "+26% YoY ✅ Beat $882M est.")
    with c2: st.metric("Q3 GMV", "$32.7B", "+25% YoY | US +43%")
    with c3: st.metric("Q3 Net Income", "−$95M", "vs +$12M prior year", delta_color="inverse")
    with c4: st.metric("Active Merchants", "850K", "+38% YoY")

    st.markdown("---")
    t1, t2, t3 = st.tabs(["📊  Revenue Growth", "📦  GMV & Profit", "👤  ARPU & Take Rate"])

    with t1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        bar_colors = [MUTED]*5 + [GOLD, GREEN]
        fig.add_trace(go.Bar(
            x=kl_annual["year"], y=kl_annual["revenue_m"],
            marker_color=bar_colors, name="Revenue ($M)",
            text=[f"${v:,.0f}M" for v in kl_annual["revenue_m"]],
            textposition="outside", textfont=dict(color="white", size=9),
        ), secondary_y=False)
        valid = kl_annual.dropna(subset=["revenue_growth"])
        fig.add_trace(go.Scatter(
            x=valid["year"], y=valid["revenue_growth"],
            mode="lines+markers", name="YoY Growth %",
            line=dict(color=GOLD, width=2, dash="dash"),
            marker=dict(size=6),
        ), secondary_y=True)
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        fig.update_yaxes(title_text="Revenue ($M)", secondary_y=False)
        fig.update_yaxes(title_text="Growth %", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=kl_qtr["quarter"], y=kl_qtr["gmv_b"],
            marker_color=BLUE, opacity=0.6, name="GMV ($B)",
        ), secondary_y=False)
        ni_colors = [GREEN if v >= 0 else RED for v in kl_qtr["net_income_m"]]
        fig.add_trace(go.Bar(
            x=kl_qtr["quarter"], y=kl_qtr["net_income_m"],
            marker_color=ni_colors, name="Net Income ($M)", opacity=0.85,
        ), secondary_y=True)
        fig.add_hline(y=0, line_color="#2A2A35", secondary_y=True)
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=380, barmode="group")
        fig.update_yaxes(title_text="GMV ($B)", secondary_y=False)
        fig.update_yaxes(title_text="Net Income ($M)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box danger">
        <span class="insight-label">Key Tension</span>
        GMV is growing strongly (+25% YoY) while net income swung from +$12M to −$95M.
        This divergence — volume up, profitability down — is the central question for KLAR's re-rating.
        Elliott Investment Management buying $6.5B in fair financing loans signals Klarna
        needs external capital to fund its own growth.
        </div>
        """, unsafe_allow_html=True)

    with t3:
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=kl_annual["year"], y=kl_annual["arpu"],
                fill="tozeroy", fillcolor="rgba(232,197,109,0.08)",
                line=dict(color=GOLD, width=2.5),
                mode="lines+markers+text",
                text=[f"${v:.1f}" for v in kl_annual["arpu"]],
                textposition="top center", textfont=dict(color=MUTED, size=9),
                name="ARPU ($)",
            ))
            fig.update_layout(
                **PLOTLY_TEMPLATE["layout"], height=320,
                title=dict(text="Avg Revenue Per User ($)", font=dict(color="white", size=12)),
                yaxis_title="ARPU ($)", showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=kl_annual["year"], y=kl_annual["take_rate"],
                fill="tozeroy", fillcolor="rgba(111,207,151,0.08)",
                line=dict(color=GREEN, width=2.5),
                mode="lines+markers+text",
                text=[f"{v:.2f}%" for v in kl_annual["take_rate"]],
                textposition="top center", textfont=dict(color=MUTED, size=9),
                name="Take Rate %",
            ))
            fig.update_layout(
                **PLOTLY_TEMPLATE["layout"], height=320,
                title=dict(text="Take Rate % (Revenue / GMV)", font=dict(color="white", size=12)),
                yaxis_title="Take Rate (%)", showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION: DEBT RISK
# ══════════════════════════════════════════════════════════════════════════════

elif section == "⚠️  Debt Risk":
    st.markdown("## § 03 — Consumer Debt Risk")
    st.markdown('<p style="color:#7a7a8a;font-size:14px;max-width:700px;line-height:1.7;">The section the earnings calls don\'t lead with. BNPL\'s rapid growth has created a population of borrowers who are invisible to traditional credit systems — and the data is beginning to show stress.</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Late Payments 2025", "41%", "+7pp vs 2024", delta_color="inverse")
    with c2: st.metric("Gen Z Late Rate", "51%", "Highest of any generation", delta_color="inverse")
    with c3: st.metric("Subprime Users", "61%", "Of all BNPL borrowers", delta_color="inverse")
    with c4: st.metric("Loan Stacking", "63%", "Multiple loans at once", delta_color="inverse")

    st.markdown("---")
    t1, t2, t3 = st.tabs(["📊  Delinquency Paradox", "👥  By Generation", "🌍  Market vs Risk"])

    with t1:
        fig = go.Figure()
        bar_colors = [GREEN, RED, GOLD, RED, ORANGE, ORANGE, GREEN]
        fig.add_trace(go.Bar(
            x=delinquency["rate"], y=delinquency["type"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v}%" for v in delinquency["rate"]],
            textposition="outside", textfont=dict(color="white", size=11),
        ))
        fig.update_layout(
            **PLOTLY_TEMPLATE["layout"], height=380,
            xaxis_title="Rate (%)", xaxis_range=[0, 50],
            title=dict(text="The Delinquency Paradox — Official vs Self-Reported", font=dict(color="white", size=13)),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box danger">
        <span class="insight-label">The Phantom Debt Problem</span>
        BNPL's official default rate (1.83%) looks stellar vs credit cards (8.8%).
        But 41% of users self-report late payments — a 22x gap. Why? BNPL loans are
        <b>not reported to credit bureaus</b>. Auto-debit masks true payment failures.
        Short repayment windows mean 'missed' is different from 'defaulted'. The Richmond
        Fed calls this 'phantom debt' — lenders making other credit decisions can't see
        a borrower's BNPL load at all.
        </div>
        """, unsafe_allow_html=True)

    with t2:
        fig = go.Figure()
        x = late_pay["demographic"]
        fig.add_trace(go.Bar(name="2024", x=x, y=late_pay["rate_2024"],
                             marker_color=GOLD, opacity=0.55))
        fig.add_trace(go.Bar(name="2025", x=x, y=late_pay["rate_2025"],
                             marker_color=RED, opacity=0.85))
        for i, row in late_pay.iterrows():
            delta = row["rate_2025"] - row["rate_2024"]
            fig.add_annotation(
                x=row["demographic"], y=row["rate_2025"] + 1.5,
                text=f"+{delta}pp", showarrow=False,
                font=dict(color=RED, size=11),
            )
        fig.update_layout(
            **PLOTLY_TEMPLATE["layout"], height=380, barmode="group",
            yaxis_title="% Reporting Late Payment",
            title=dict(text="BNPL Late Payment Rate by Generation — 2024 vs 2025", font=dict(color="white", size=13)),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        <span class="insight-label">Generational Risk</span>
        Gen Z's 51% late payment rate is the single most alarming data point in this project.
        These are first-time credit users who are learning financial habits through BNPL —
        a product that doesn't report to credit bureaus, doesn't build credit history, but
        does charge late fees. The 7pp YoY increase across all generations suggests this is
        a structural trend, not a blip.
        </div>
        """, unsafe_allow_html=True)

    with t3:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        actuals = market_size[~market_size["projected"]]
        projections = market_size[market_size["projected"]]

        for df, dash, opacity in [(actuals, "solid", 1.0), (projections, "dash", 0.7)]:
            fig.add_trace(go.Scatter(
                x=df["year"], y=df["global_b"],
                mode="lines+markers", line=dict(color=GOLD, width=2.5, dash=dash),
                opacity=opacity, name="Global GMV" if dash == "solid" else "Global GMV (proj.)",
                showlegend=dash == "solid",
            ), secondary_y=False)
            fig.add_trace(go.Scatter(
                x=df["year"], y=df["us_b"],
                mode="lines+markers", line=dict(color=BLUE, width=2, dash=dash),
                opacity=opacity, name="US Market" if dash == "solid" else "US Market (proj.)",
                showlegend=dash == "solid",
            ), secondary_y=False)

        late_trend = pd.DataFrame({
            "year": [2021, 2022, 2023, 2024, 2025],
            "pct":  [22, 26, 30, 34, 41]
        })
        fig.add_trace(go.Scatter(
            x=late_trend["year"], y=late_trend["pct"],
            mode="lines+markers", line=dict(color=RED, width=2, dash="dashdot"),
            marker=dict(symbol="triangle-up", size=8),
            name="Late Payments %",
        ), secondary_y=True)

        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=400)
        fig.update_yaxes(title_text="Market Size ($B)", secondary_y=False)
        fig.update_yaxes(title_text="Late Payment Rate (%)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION: COMPETITORS
# ══════════════════════════════════════════════════════════════════════════════

elif section == "🏆 Competitors":
    st.markdown("## § 04 — Competitive Landscape")

    c1, c2, c3, c4 = st.columns(4)
    for col, row in zip([c1, c2, c3, c4], competitors.itertuples()):
        with col:
            st.metric(
                f"{row.company} ({row.ticker})",
                f"${row.mktcap_b:.1f}B mktcap",
                f"{row.ret_since_ipo:+}% since KLAR IPO",
                delta_color="normal" if row.ret_since_ipo >= 0 else "inverse"
            )

    st.markdown("---")
    t1, t2, t3 = st.tabs(["📊  Valuation & Growth", "🔥  Scorecard", "🔗  Correlation"])

    with t1:
        col1, col2, col3 = st.columns(3)

        with col1:
            fig = go.Figure(go.Bar(
                x=competitors["ticker"], y=competitors["ps_ratio"],
                marker_color=[TICKER_COLORS[t] for t in competitors["ticker"]],
                text=[f"{v:.2f}x" for v in competitors["ps_ratio"]],
                textposition="outside", textfont=dict(color="white"),
            ))
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=300, showlegend=False,
                              title=dict(text="P/S Ratio", font=dict(color="white", size=12)))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure(go.Bar(
                x=competitors["ticker"], y=competitors["rev_growth"],
                marker_color=[TICKER_COLORS[t] for t in competitors["ticker"]],
                text=[f"{v}%" for v in competitors["rev_growth"]],
                textposition="outside", textfont=dict(color="white"),
            ))
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=300, showlegend=False,
                              title=dict(text="Revenue Growth YoY", font=dict(color="white", size=12)))
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            ret_colors = [GREEN if v >= 0 else RED for v in competitors["ret_since_ipo"]]
            fig = go.Figure(go.Bar(
                x=competitors["ticker"], y=competitors["ret_since_ipo"],
                marker_color=ret_colors,
                text=[f"{v:+}%" for v in competitors["ret_since_ipo"]],
                textposition="outside", textfont=dict(color="white"),
            ))
            fig.add_hline(y=0, line_color="#2A2A35")
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=300, showlegend=False,
                              title=dict(text="Return Since KLAR IPO", font=dict(color="white", size=12)))
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        scorecard_data = {
            "Metric":           ["Revenue Growth","P/S (lower=better)","Profitability","User Scale","Stock Perf","Reg. Risk","AI Invest","Credit Quality"],
            "KLAR":             [5, 4, 1, 5, 1, 2, 5, 3],
            "AFRM":             [5, 3, 3, 3, 4, 3, 3, 4],
            "PYPL":             [2, 5, 5, 5, 2, 4, 3, 5],
            "SQ":               [2, 3, 2, 3, 3, 3, 3, 3],
        }
        sc = pd.DataFrame(scorecard_data)

        SCORECARD_TICKERS = {"KLAR": GOLD, "AFRM": GREEN, "PYPL": BLUE, "SQ": ORANGE}
        fig = go.Figure()
        for ticker, color in SCORECARD_TICKERS.items():
            fig.add_trace(go.Bar(
                name=ticker, x=sc["Metric"], y=sc[ticker],
                marker_color=color, opacity=0.85,
            ))
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=400, barmode="group",
                          title=dict(text="Competitor Scorecard (1-5 per metric)", font=dict(color="white", size=13)))
        fig.update_yaxes(tickvals=[1,2,3,4,5], ticktext=["Poor","Below Avg","Average","Good","Excellent"])
        st.plotly_chart(fig, use_container_width=True)

        totals = {t: sum(scorecard_data[t]) for t in ["KLAR","AFRM","PYPL","SQ"]}
        cols = st.columns(4)
        for col, (ticker, total) in zip(cols, totals.items()):
            with col:
                st.metric(f"{ticker} Total", f"{total}/40")

    with t3:
        if live_data_ok:
            # Only use columns that actually exist in returns
            avail_tickers = [t for t in ["KLAR","AFRM","PYPL","SQ","^GSPC"] if t in returns.columns]
            if len(avail_tickers) < 2:
                st.info("Not enough ticker data for correlation matrix yet. Try refreshing.")
            else:
                corr = returns[avail_tickers].corr()
                labels = {"KLAR":"Klarna","AFRM":"Affirm","PYPL":"PayPal","SQ":"Block","^GSPC":"S&P 500"}
                tick_labels = [labels[t] for t in corr.columns]
                fig = go.Figure(go.Heatmap(
                    z=corr.values, x=tick_labels, y=tick_labels,
                    colorscale="RdYlGn", zmin=-1, zmax=1,
                    text=corr.round(2).values,
                    texttemplate="%{text}",
                    textfont=dict(color="white", size=12),
                ))
                fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=400,
                                  title=dict(text="Returns Correlation Matrix", font=dict(color="white", size=13)))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Live data needed for correlation matrix.")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION: VERDICT
# ══════════════════════════════════════════════════════════════════════════════

elif section == "📋 Verdict":
    st.markdown("## § 05 — The Verdict")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style='background:#111116;border:1px solid #2a2a35;border-top:3px solid {GREEN};
                    padding:24px;border-radius:4px;height:320px;'>
            <div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;
                        color:{GREEN};margin-bottom:12px;'>Bull Case</div>
            <div style='font-size:22px;font-weight:bold;color:{GREEN};margin-bottom:16px;'>$43–55</div>
            <div style='font-size:13px;color:#7a7a8a;line-height:1.8;'>
            Revenue growing 26% YoY. US GMV +43%. 14/14 analysts say Buy.
            Trading at ~2.2x revenue vs peers at 4-6x. 5M debit card waitlist =
            untapped monetisation. Q4 earnings (Feb 25) could re-rate the stock.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background:#111116;border:1px solid #2a2a35;border-top:3px solid {GOLD};
                    padding:24px;border-radius:4px;height:320px;'>
            <div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;
                        color:{GOLD};margin-bottom:12px;'>Base Case</div>
            <div style='font-size:22px;font-weight:bold;color:{GOLD};margin-bottom:16px;'>$20–35</div>
            <div style='font-size:13px;color:#7a7a8a;line-height:1.8;'>
            Range-bound near-term. Class-action lawsuits create overhang.
            ARPU declining while user count grows = monetisation puzzle unsolved.
            Without bureau reporting, macro stress could expose hidden defaults.
            Needs a clean Q4 quarter to break out.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='background:#111116;border:1px solid #2a2a35;border-top:3px solid {RED};
                    padding:24px;border-radius:4px;height:320px;'>
            <div style='font-size:10px;letter-spacing:2px;text-transform:uppercase;
                        color:{RED};margin-bottom:12px;'>Bear Case</div>
            <div style='font-size:22px;font-weight:bold;color:{RED};margin-bottom:16px;'>$10–14</div>
            <div style='font-size:13px;color:#7a7a8a;line-height:1.8;'>
            41% users missed payments in 2025. 61% subprime. Recession exposes
            phantom debt problem at scale. Class-action damages material.
            Revenue per user declining while operating losses persist =
            burning cash on growth that does not compound.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## Social Impact")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="insight-box">
        <span class="insight-label">The Consumer Side</span>
        BNPL has democratized access to short-term credit for millions who
        don't qualify for credit cards. But 61% of users being subprime, and
        Gen Z at 51% late payments, means the product risks becoming a debt
        multiplier for the most financially vulnerable — especially since it
        builds no credit history and remains invisible to scoring models.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="insight-box">
        <span class="insight-label">The Regulatory Response</span>
        CFPB's Jan and Dec 2025 reports are pre-rulemaking groundwork.
        The most likely outcome: mandatory credit bureau reporting for BNPL.
        This would transform underwriting models industry-wide, surface true
        default rates for the first time, and potentially slow BNPL's growth
        among the subprime segment that currently drives its adoption numbers.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Data sources: Klarna SEC F-1, CFPB BNPL Reports Jan/Dec 2025, NY Fed Q1 2025, Morgan Stanley AlphaWise, LendingTree Survey 2025, Richmond Fed EB-25-03, Yahoo Finance. Not financial advice.")
