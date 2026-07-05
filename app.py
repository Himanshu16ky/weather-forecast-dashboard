# app.py — Main entry point
# Weather Forecast MLOps Dashboard

import streamlit as st

st.set_page_config(
    page_title  = "Weather Forecast — India",
    page_icon   = "🌦️",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ═══════════════════════════════════════════════════════════════
       FONTS
       ═══════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #FFFFFF !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       APP BACKGROUND — radial gradient
       ═══════════════════════════════════════════════════════════════ */
    .stApp {
        background: #050816;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(96,165,250,0.15) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 50%, rgba(139,92,246,0.08) 0%, transparent 50%),
            radial-gradient(ellipse 50% 30% at 20% 80%, rgba(96,165,250,0.06) 0%, transparent 40%);
    }

    /* ═══════════════════════════════════════════════════════════════
       HIDE DEFAULT STREAMLIT PAGE NAVIGATION (fixes duplicate sidebar)
       ═══════════════════════════════════════════════════════════════ */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       SIDEBAR — dark gradient
       ═══════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #050816 100%) !important;
        border-right: 1px solid rgba(96,165,250,0.1);
    }
    [data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(96,165,250,0.2) !important;
        border-radius: 10px;
    }
    [data-testid="stSidebar"] input {
        color: #E2E8F0 !important;
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(96,165,250,0.2) !important;
        border-radius: 10px;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        color: rgba(203,213,225,0.7) !important;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(96,165,250,0.12) !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       METRIC CARDS — dark glassmorphism
       ═══════════════════════════════════════════════════════════════ */
    .metric-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(96,165,250,0.12);
        border-radius: 20px;
        padding: 1.4rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #60A5FA, #8B5CF6);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(96,165,250,0.3);
        box-shadow: 0 8px 32px rgba(96,165,250,0.1);
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-card .icon {
        font-size: 1.6rem;
        margin-bottom: 0.6rem;
        display: block;
    }
    .metric-card .label {
        font-size: 0.72rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        line-height: 1.2;
    }
    .metric-card .unit {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 400;
        margin-left: 0.3rem;
    }

    /* ═══════════════════════════════════════════════════════════════
       GRADIENT TEXT
       ═══════════════════════════════════════════════════════════════ */
    .gradient-text {
        background: linear-gradient(135deg, #60A5FA 0%, #8B5CF6 50%, #60A5FA 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient-shift 4s ease infinite;
    }
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 100% center; }
    }

    /* ═══════════════════════════════════════════════════════════════
       NAV CARDS
       ═══════════════════════════════════════════════════════════════ */
    .nav-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(96,165,250,0.1);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .nav-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96,165,250,0.3);
        box-shadow: 0 4px 24px rgba(96,165,250,0.08);
        background: rgba(96,165,250,0.05);
    }
    .nav-card .nav-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .nav-card .nav-title {
        font-size: 1rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 0.25rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .nav-card .nav-desc {
        font-size: 0.8rem;
        color: #64748B;
        line-height: 1.4;
    }

    /* ═══════════════════════════════════════════════════════════════
       SECTION DIVIDERS
       ═══════════════════════════════════════════════════════════════ */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(96,165,250,0.2), transparent);
        margin: 2.5rem 0;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ═══════════════════════════════════════════════════════════════
       HIDE DEFAULT STREAMLIT ELEMENTS
       ═══════════════════════════════════════════════════════════════ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {
        background: rgba(5,8,22,0.8);
        backdrop-filter: blur(12px);
    }

    /* ═══════════════════════════════════════════════════════════════
       HORIZONTAL RULE OVERRIDE
       ═══════════════════════════════════════════════════════════════ */
    hr {
        border-color: rgba(96,165,250,0.1) !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       SCROLLBAR
       ═══════════════════════════════════════════════════════════════ */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #050816;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(96,165,250,0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(96,165,250,0.5);
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.5rem 0;">
        <div style="font-size: 1.6rem; margin-bottom: 0.3rem;">🌦️</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem;
                    font-weight: 700; color: #FFFFFF !important; letter-spacing: -0.01em;">
            Weather Forecast
        </div>
        <div style="font-size: 0.72rem; color: #64748B !important;
                    text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.15rem;">
            MLOps Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <div style="font-size: 0.72rem; color: #64748B !important; text-transform: uppercase;
                    letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.8rem;">
            Navigation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("app.py", label="Overview", use_container_width=True)
    st.page_link("pages/1_Forecast.py", label="Forecast", use_container_width=True)
    st.page_link("pages/2_Performance.py", label="Performance", use_container_width=True)

    st.markdown("---")

    st.markdown("""
    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(96,165,250,0.06);
                border: 1px solid rgba(96,165,250,0.12); border-radius: 12px;">
        <div style="font-size: 0.72rem; color: #64748B !important; text-transform: uppercase;
                    letter-spacing: 0.08em; margin-bottom: 0.4rem; font-weight: 500;">
            System Status
        </div>
        <div style="display: flex; align-items: center; gap: 0.4rem; margin-top: 0.3rem;">
            <div style="width: 7px; height: 7px; border-radius: 50%; background: #34D399;
                        box-shadow: 0 0 8px rgba(52,211,153,0.5);"></div>
            <span style="font-size: 0.8rem; color: #CBD5E1 !important;">All systems operational</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Hero Section — Centered ──────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 4rem 0 2rem 0; max-width: 720px; margin: 0 auto;">
    <h1 style="font-size: 3.6rem; font-weight: 800; margin: 0 0 1rem 0;
               line-height: 1.15; letter-spacing: -0.03em; font-family: 'Space Grotesk', sans-serif !important;">
        Weather Forecast<br>
        <span class="gradient-text">India</span>
    </h1>
    <p style="font-size: 1.08rem; color: #94A3B8; line-height: 1.75;
              margin: 0 auto; font-weight: 400; max-width: 600px;">
        An enterprise-grade MLOps pipeline forecasting temperature, wind speed, humidity,
        cloud cover, and precipitation for <span style="color: #CBD5E1; font-weight: 500;">7 major Indian cities</span>
        — <span style="color: #CBD5E1; font-weight: 500;">72 hours ahead</span>,
        retrained and deployed daily with full model versioning.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Metric Cards — Centered ──────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <span class="icon">🏙️</span>
        <div class="label">Cities Covered</div>
        <div class="value">7<span class="unit">cities</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <span class="icon">🎯</span>
        <div class="label">Forecast Horizon</div>
        <div class="value">72<span class="unit">hours</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <span class="icon">📊</span>
        <div class="label">Training Data</div>
        <div class="value">7<span class="unit">years hourly</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <span class="icon">🔄</span>
        <div class="label">Update Frequency</div>
        <div class="value">Daily<span class="unit">1 AM IST</span></div>
    </div>
    """, unsafe_allow_html=True)


# ── Section Divider ───────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ── Platform Navigation — Centered ───────────────────────────────────────────
st.markdown('<div class="section-title" style="justify-content: center;">🧭 Platform Navigation</div>', unsafe_allow_html=True)

nav_left, nav_right = st.columns(2, gap="large")

with nav_left:
    st.markdown("""
    <div class="nav-card">
        <span class="nav-icon">🔮</span>
        <div class="nav-title">Forecast Dashboard</div>
        <div class="nav-desc">72-hour predictions per city and model — temperature, wind, humidity, clouds, and precipitation with interactive day-by-day views.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Forecast.py", label="Open Forecast →", use_container_width=True)

with nav_right:
    st.markdown("""
    <div class="nav-card">
        <span class="nav-icon">📊</span>
        <div class="nav-title">Model Performance</div>
        <div class="nav-desc">Test set evaluation with MAE/RMSE metrics, horizon degradation analysis, and multi-model comparison across all weather variables.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Performance.py", label="Open Performance →", use_container_width=True)


# ── Footer spacer ────────────────────────────────────────────────────────────
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
