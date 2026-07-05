# pages/1_Forecast.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from datetime import date, timedelta
from html import escape

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import (
    get_available_models, get_available_dates,
    load_predictions, CITIES, TARGET_LABELS, TARGET_ICONS, TARGET_COLORS,
    champion_label,
)

st.set_page_config(page_title="Forecast — Weather India", page_icon="🔮", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #FFFFFF !important;
}

/* App background */
.stApp {
    background: #050816;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(96,165,250,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 50%, rgba(139,92,246,0.05) 0%, transparent 50%);
}

/* Hide default Streamlit page navigation (fixes duplicate sidebar) */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #050816 100%) !important;
    border-right: 1px solid rgba(96,165,250,0.1);
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * { color: #E2E8F0 !important; }
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
[data-testid="stSidebar"] hr { border-color: rgba(96,165,250,0.12) !important; }

/* Cards */
.day-card {
    border-radius: 16px;
    padding: 1rem 0.8rem;
    text-align: center;
    border: 1px solid rgba(96,165,250,0.1);
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.day-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(96,165,250,0.08);
}
.day-card.active {
    border-color: rgba(96,165,250,0.4);
    background: rgba(96,165,250,0.08);
    box-shadow: 0 0 24px rgba(96,165,250,0.1);
}
.day-card.inactive {
    background: rgba(255,255,255,0.02);
    border-color: rgba(255,255,255,0.06);
}

.param-card {
    border-radius: 16px;
    padding: 0.9rem 1rem;
    text-align: center;
    margin-bottom: 0.4rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(96,165,250,0.1);
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}
.param-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(96,165,250,0.06);
}

.emoji-row {
    font-size: 1.1rem;
    letter-spacing: 0.05em;
    line-height: 2;
    padding: 0.5rem 0;
    overflow-x: auto;
    white-space: nowrap;
}

/* Hide defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header[data-testid="stHeader"] {
    background: rgba(5,8,22,0.8);
    backdrop-filter: blur(12px);
}
hr { border-color: rgba(96,165,250,0.1) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050816; }
::-webkit-scrollbar-thumb { background: rgba(96,165,250,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(96,165,250,0.5); }

/* Expander */
.streamlit-expanderHeader { color: #CBD5E1 !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --cyan: #00C8FF;
    --purple: #9D4EDD;
    --pink: #FF4D8D;
    --green: #00F5A0;
    --orange: #FFB547;
}

html, body, [class*="css"] { letter-spacing: 0; }

.stApp {
    background: #030712;
    background-image:
        radial-gradient(ellipse at 28% -10%, rgba(0,200,255,0.20) 0%, transparent 34%),
        radial-gradient(ellipse at 88% 8%, rgba(157,78,221,0.16) 0%, transparent 32%),
        radial-gradient(ellipse at 48% 98%, rgba(0,245,160,0.08) 0%, transparent 38%),
        radial-gradient(circle at 15% 18%, rgba(255,255,255,0.10) 0 1px, transparent 1.5px),
        radial-gradient(circle at 72% 22%, rgba(255,255,255,0.08) 0 1px, transparent 1.5px),
        radial-gradient(circle at 40% 64%, rgba(255,255,255,0.07) 0 1px, transparent 1.5px),
        linear-gradient(180deg, #050816 0%, #030712 52%, #070B1A 100%);
    background-attachment: fixed;
}

.block-container {
    max-width: 1220px;
    padding-top: 2.25rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(5,8,22,0.96), rgba(3,7,18,0.98)) !important;
    border-right: 1px solid rgba(0,200,255,0.16);
    box-shadow: 18px 0 48px rgba(0,0,0,0.28);
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
[data-testid="stSidebar"] input {
    background: rgba(8,13,31,0.78) !important;
    border: 1px solid rgba(0,200,255,0.24) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 0 0 1px rgba(157,78,221,0.05);
}
[data-testid="stSidebar"] [data-testid="stPageLink"] {
    border-radius: 12px;
    transition: transform 180ms ease, background 180ms ease, box-shadow 180ms ease;
}
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
    transform: translateX(3px);
    background: rgba(0,200,255,0.08);
    box-shadow: 0 0 22px rgba(0,200,255,0.08);
}

.sidebar-brand { padding: 0.9rem 0.25rem 1rem; }
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.sidebar-mark {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, rgba(0,200,255,0.22), rgba(157,78,221,0.22));
    border: 1px solid rgba(0,200,255,0.32);
    box-shadow: 0 0 26px rgba(0,200,255,0.16);
    font-size: 1.45rem;
}
.sidebar-title {
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    line-height: 1.05;
}
.sidebar-subtitle {
    color: #7DD3FC !important;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.16rem;
}
.sidebar-status {
    margin-top: 1.2rem;
    padding: 1rem;
    border-radius: 14px;
    background: linear-gradient(180deg, rgba(15,23,42,0.74), rgba(8,13,31,0.72));
    border: 1px solid rgba(0,245,160,0.18);
    box-shadow: 0 16px 34px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.05);
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #00F5A0;
    box-shadow: 0 0 18px rgba(0,245,160,0.8);
    display: inline-block;
    margin-right: 0.48rem;
}

.forecast-hero {
    position: relative;
    overflow: hidden;
    border-radius: 28px;
    padding: 1.6rem;
    margin: 0.25rem 0 1.8rem;
    background:
        linear-gradient(135deg, rgba(15,23,42,0.72), rgba(8,13,31,0.50)) padding-box,
        linear-gradient(135deg, rgba(0,200,255,0.55), rgba(157,78,221,0.45), rgba(255,77,141,0.30)) border-box;
    border: 1px solid transparent;
    box-shadow: 0 24px 80px rgba(0,0,0,0.34), 0 0 56px rgba(0,200,255,0.08);
    backdrop-filter: blur(18px);
    animation: fade-up 520ms ease both;
}
.forecast-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(115deg, transparent 0%, rgba(255,255,255,0.08) 42%, transparent 58%),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 84px);
    opacity: 0.42;
    pointer-events: none;
}
.hero-grid {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr);
    gap: 1.2rem;
    align-items: center;
}
.hero-kicker {
    color: #7DD3FC;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}
.hero-title {
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: clamp(2.45rem, 5vw, 4.8rem);
    line-height: 0.94;
    color: #FFFFFF;
}
.hero-title span {
    background: linear-gradient(110deg, #00C8FF 0%, #9D4EDD 52%, #FF4D8D 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 18px rgba(0,200,255,0.20));
}
.hero-line {
    width: min(440px, 84%);
    height: 3px;
    border-radius: 999px;
    margin-top: 1rem;
    background: linear-gradient(90deg, #00C8FF, #9D4EDD, #FF4D8D, transparent);
    box-shadow: 0 0 22px rgba(0,200,255,0.36);
    animation: shimmer 3.8s ease-in-out infinite;
}
.hero-copy {
    color: #94A3B8;
    font-size: 0.98rem;
    line-height: 1.7;
    max-width: 690px;
    margin-top: 1rem;
}
.hero-side {
    justify-self: stretch;
    min-height: 220px;
    border-radius: 22px;
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.10);
    background:
        radial-gradient(ellipse at 50% 20%, rgba(0,200,255,0.18), transparent 56%),
        linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.025));
    display: grid;
    place-items: center;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}
.weather-glyph {
    font-size: clamp(4.8rem, 10vw, 7.8rem);
    filter: drop-shadow(0 0 26px rgba(0,200,255,0.45));
    animation: float 5.5s ease-in-out infinite;
}
.meta-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.62rem;
    margin-top: 1.15rem;
}
.meta-pill {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.42rem;
    border-radius: 999px;
    padding: 0.48rem 0.75rem;
    color: #DDEAFE;
    font-size: 0.78rem;
    font-weight: 700;
    background:
        linear-gradient(135deg, rgba(8,13,31,0.78), rgba(15,23,42,0.64)) padding-box,
        linear-gradient(135deg, rgba(0,200,255,0.58), rgba(157,78,221,0.36)) border-box;
    border: 1px solid transparent;
    box-shadow: 0 10px 28px rgba(0,0,0,0.18);
    overflow: hidden;
}
.meta-pill::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(110deg, transparent, rgba(255,255,255,0.18), transparent);
    transform: translateX(-120%);
    animation: pill-sweep 5.2s ease-in-out infinite;
}
.meta-pill.champion {
    color: #FFE3A8;
    background:
        linear-gradient(135deg, rgba(40,27,8,0.84), rgba(15,23,42,0.58)) padding-box,
        linear-gradient(135deg, rgba(255,181,71,0.72), rgba(255,77,141,0.34)) border-box;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: 2.1rem 0 1rem;
}
.section-title {
    margin: 0;
    color: #F8FAFC;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 1.35rem;
}
.section-eyebrow {
    color: #7DD3FC;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 800;
}

.metric-card {
    position: relative;
    overflow: hidden;
    min-height: 154px;
    margin-bottom: 1.2rem;
    border-radius: 22px;
    padding: 1.2rem;
    background:
        linear-gradient(180deg, rgba(15,23,42,0.82), rgba(8,13,31,0.70)) padding-box,
        linear-gradient(135deg, var(--accent), rgba(255,255,255,0.10), rgba(157,78,221,0.28)) border-box;
    border: 1px solid transparent;
    box-shadow: 0 18px 42px rgba(0,0,0,0.26);
    backdrop-filter: blur(18px);
    transition: transform 220ms ease, box-shadow 220ms ease, filter 220ms ease;
}
.metric-card:hover {
    transform: translateY(-6px) scale(1.012);
    box-shadow: 0 24px 58px rgba(0,0,0,0.34), 0 0 34px rgba(0,200,255,0.18);
}

.metric-card.feature {
    min-height: 332px;
    padding: 1.45rem;
}
.metric-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.8rem;
}
.metric-icon {
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    border-radius: 17px;
    background: rgba(255,255,255,0.065);
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 0 28px rgba(0,200,255,0.12);
    font-size: 1.7rem;
}
.metric-card.feature .metric-icon {
    width: 72px;
    height: 72px;
    font-size: 2.4rem;
    border-radius: 22px;
}
.metric-label {
    color: #94A3B8;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
    margin-top: 1rem;
}
.metric-value {
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.05rem;
    line-height: 1;
    font-weight: 800;
    margin-top: 0.34rem;
    transition: transform 220ms ease;
}
.metric-card:hover .metric-value { transform: scale(1.035); }
.metric-card.feature .metric-value {
    font-size: clamp(4rem, 8vw, 6.5rem);
    margin-top: 1.4rem;
}
.metric-unit {
    color: #64748B;
    font-size: 0.78rem;
    font-weight: 800;
    margin-top: 0.38rem;
}
.metric-chip {
    border-radius: 999px;
    color: #DDEAFE;
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.3rem 0.55rem;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
}

.day-card {
    position: relative;
    overflow: hidden;
    min-height: 200px;
    border-radius: 22px;
    padding: 1.15rem;
    text-align: left;
    background:
        linear-gradient(180deg, rgba(15,23,42,0.78), rgba(8,13,31,0.66)) padding-box,
        linear-gradient(135deg, rgba(0,200,255,0.32), rgba(157,78,221,0.24), rgba(255,255,255,0.08)) border-box;
    border: 1px solid transparent;
    box-shadow: 0 18px 42px rgba(0,0,0,0.22);
    backdrop-filter: blur(16px);
    transition: transform 220ms ease, box-shadow 220ms ease;
}
.day-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 24px 58px rgba(0,0,0,0.30), 0 0 34px rgba(0,200,255,0.14);
}
.day-card.active {
    background:
        linear-gradient(135deg, rgba(0,200,255,0.18), rgba(157,78,221,0.18), rgba(8,13,31,0.72)) padding-box,
        linear-gradient(135deg, #00C8FF, #9D4EDD, #FF4D8D) border-box;
    box-shadow: 0 24px 64px rgba(0,0,0,0.32), 0 0 42px rgba(0,200,255,0.22);
}
.day-card.active::after {
    content: "";
    position: absolute;
    inset: 8px;
    border-radius: 18px;
    border: 1px solid rgba(0,200,255,0.20);
    animation: pulse-ring 2.6s ease-in-out infinite;
    pointer-events: none;
}
.day-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.8rem;
}
.day-name {
    color: #7DD3FC;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 900;
}
.day-date {
    color: #E2E8F0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    margin-top: 0.16rem;
}
.day-check {
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 999px;
    background: linear-gradient(135deg, #00C8FF, #9D4EDD);
    color: #FFFFFF;
    font-size: 0.82rem;
    box-shadow: 0 0 24px rgba(0,200,255,0.38);
}
.day-glyph {
    font-size: 3rem;
    margin: 1rem 0 0.55rem;
    filter: drop-shadow(0 0 18px rgba(0,200,255,0.22));
}
.day-temp {
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 1.78rem;
    line-height: 1;
}
.day-temp span {
    color: #64748B;
    font-size: 1rem;
    font-weight: 700;
}
.day-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.8rem;
}
.day-mini {
    color: #CBD5E1;
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 999px;
    padding: 0.35rem 0.52rem;
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.08);
}

.health-panel {
    margin: 1.25rem 0 0.4rem;
    border-radius: 22px;
    padding: 1rem;
    background:
        linear-gradient(180deg, rgba(15,23,42,0.72), rgba(8,13,31,0.62)) padding-box,
        linear-gradient(135deg, rgba(0,245,160,0.32), rgba(0,200,255,0.22), rgba(157,78,221,0.24)) border-box;
    border: 1px solid transparent;
    box-shadow: 0 20px 48px rgba(0,0,0,0.25);
}
.health-grid {
    display: grid;
    grid-template-columns: 1.1fr repeat(3, 0.8fr);
    gap: 0.8rem;
}
.health-card {
    min-height: 84px;
    border-radius: 16px;
    padding: 0.82rem;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
}

.health-label {
    color: #94A3B8;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 900;
}
.health-value {
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.38rem;
    font-weight: 800;
    margin-top: 0.25rem;
}
.health-note {
    color: #64748B;
    font-size: 0.72rem;
    margin-top: 0.22rem;
}

.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(0,200,255,0.24) !important;
    background: rgba(8,13,31,0.72) !important;
    color: #E2E8F0 !important;
    transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(0,200,255,0.58) !important;
    box-shadow: 0 0 26px rgba(0,200,255,0.18);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00C8FF, #9D4EDD) !important;
    border-color: rgba(255,255,255,0.22) !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 28px rgba(0,200,255,0.28);
}

header[data-testid="stHeader"] {
    background: rgba(3,7,18,0.72);
    backdrop-filter: blur(12px);
}
hr {
    border-color: rgba(0,200,255,0.10) !important;
    margin: 1.75rem 0 !important;
}
::-webkit-scrollbar-track { background: #030712; }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.35); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(157,78,221,0.55); }

@keyframes fade-up {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes float {
    0%, 100% { transform: translateY(0) rotate(-2deg); }
    50% { transform: translateY(-10px) rotate(2deg); }
}
@keyframes shimmer {
    0%, 100% { opacity: 0.72; filter: saturate(1); }
    50% { opacity: 1; filter: saturate(1.5); }
}
@keyframes pill-sweep {
    0%, 78% { transform: translateX(-120%); }
    100% { transform: translateX(120%); }
}
@keyframes pulse-soft {
    0%, 100% { opacity: 0.42; transform: scaleX(0.96); }
    50% { opacity: 0.76; transform: scaleX(1); }
}
@keyframes pulse-ring {
    0%, 100% { opacity: 0.35; transform: scale(0.99); }
    50% { opacity: 0.88; transform: scale(1.01); }
}

@media (max-width: 900px) {
    .hero-grid,
    .health-grid {
        grid-template-columns: 1fr;
    }
    .hero-side { min-height: 150px; }
    .metric-card.feature { min-height: 240px; }
}
</style>
""", unsafe_allow_html=True)

# def cloud_emoji(cover_pct: float) -> str:
#     if cover_pct is None: return "🌡️"
#     if cover_pct < 20:   return "☀️"
#     elif cover_pct < 30: return "🌤️"
#     elif cover_pct < 60: return "⛅"
#     elif cover_pct < 85: return "🌥️"
#     else:                return "☁️"

def weather_emoji(cover_pct: float, precip: float, hour: int = None) -> str:
    is_night = False
    if hour is not None and (hour < 6 or hour >= 18):
        is_night = True

    if precip is not None and precip > 0.1:  # Threshold for noticeable rain
        return "🌧️"
    if cover_pct is None: return "🌡️"
    
    if is_night:
        if cover_pct < 30:   return "🌙"
        else:                return "☁️"
    else:
        if cover_pct < 20:   return "☀️"
        elif cover_pct < 30: return "🌤️"
        elif cover_pct < 60: return "⛅"
        elif cover_pct < 85: return "🌥️"
        else:                return "☁️"
    
FONT = "Inter, 'Space Grotesk', sans-serif"
GRID = "rgba(255,255,255,0.08)"

def make_chart(df: pd.DataFrame, target: str, color: str, height: int = 300) -> go.Figure:
    label = TARGET_LABELS[target]
    
    # 1. Convert hex to RGB tuples for fill opacity
    hex_c = color.lstrip('#')
    r, g, b = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
    
    fig = go.Figure()

    # Outer glow trace
    fig.add_trace(go.Scatter(
        x=df["forecast_timestamp"],
        y=df[f"pred_{target}"],
        mode="lines",
        line=dict(color=f"rgba({r}, {g}, {b}, 0.15)", width=12, shape="spline"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Inner glow trace
    fig.add_trace(go.Scatter(
        x=df["forecast_timestamp"],
        y=df[f"pred_{target}"],
        mode="lines",
        line=dict(color=f"rgba({r}, {g}, {b}, 0.4)", width=6, shape="spline"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Main trace
    fig.add_trace(go.Scatter(
        x=df["forecast_timestamp"],
        y=df[f"pred_{target}"],
        mode="lines",
        line=dict(color=color, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba({r}, {g}, {b}, 0.08)",
        hovertemplate=f"<b>%{{x|%H:%M}}</b><br><span style='font-size:1.1em; color:{color}'>{label}: %{{y:.1f}}</span><extra></extra>",
    ))
    
    # 2. Add current hour highlight
    now = pd.Timestamp.now().replace(minute=0, second=0, microsecond=0)
    
    current_hour_mask = df["forecast_timestamp"] == now
    if current_hour_mask.any():
        start_time = now
        end_time = now + pd.Timedelta(hours=1)
        val = df.loc[current_hour_mask, f"pred_{target}"].values[0]
        
        fig.add_vrect(
            x0=start_time, x1=end_time,
            fillcolor=f"rgba({r}, {g}, {b}, 0.12)",
            layer="below", 
            line_width=1, 
            line_color=f"rgba({r}, {g}, {b}, 0.4)", 
            line_dash="dash"
        )
        
        fig.add_annotation(
            x=start_time + pd.Timedelta(minutes=30),
            y=val,
            text=f"<b>{val:.1f}</b>",
            showarrow=False,
            yshift=24,
            font=dict(color=color, size=14, family="'Space Grotesk', sans-serif")
        )

    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color="#94A3B8"),
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", 
            showgrid=True, 
            zeroline=False, 
            tickformat="%H:%M",
            tickfont=dict(color="#64748B", size=11),
            showline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", 
            showgrid=True, 
            zeroline=False, 
            title=label,
            titlefont=dict(color="#64748B", size=11), 
            tickfont=dict(color="#64748B", size=11),
            showline=False,
        ),
        hovermode="x unified", 
        showlegend=False,
        hoverlabel=dict(
            bgcolor="rgba(8,13,31,0.85)",
            bordercolor=f"rgba({r}, {g}, {b}, 0.4)",
            font=dict(family=FONT, color="#E2E8F0", size=13),
        )
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">
            <div class="sidebar-mark">☁️</div>
            <div>
                <div class="sidebar-title">Weather AI</div>
                <div class="sidebar-subtitle">MLOps Console</div>
            </div>
        </div>
    </div>
    <div style="margin: 0.35rem 0 1rem;">
        <div style="font-size: 0.72rem; color: #7DD3FC !important; text-transform: uppercase;
                    letter-spacing: 0.14em; font-weight: 800; margin-bottom: 0.8rem;">
            Navigation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("app.py", label="Overview", use_container_width=True)
    st.page_link("pages/1_Forecast.py", label="Forecast", use_container_width=True)
    st.page_link("pages/2_Performance.py", label="Performance", use_container_width=True)

    st.markdown("---")
    models = get_available_models()
    if not models:
        st.error("No Production models found.")
        st.stop()
# original line was model_labels = [m["label"] for m in models]
    model_labels = [champion_label(m) for m in models]
    sel_idx      = st.selectbox("Model", range(len(model_labels)),
                                format_func=lambda i: model_labels[i])
    sel_model    = models[sel_idx]
    model_key    = sel_model["model_key"]
    city         = st.selectbox("City", CITIES)
    avail_dates  = get_available_dates(model_key, city)
    if not avail_dates:
        st.error("No predictions available yet.")
        st.stop()
        
    avail_dates_dt = [date.fromisoformat(d) for d in avail_dates]
    min_date = min(avail_dates_dt)
    max_date = max(avail_dates_dt)
    
    run_date_dt = st.date_input(
        "Forecast date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )
    run_date = run_date_dt.isoformat()
    
    if run_date not in avail_dates:
        st.warning(f"No predictions available for {run_date}. Please select another date.")
        st.stop()

    st.markdown(f"""
    <div class="sidebar-status">
        <div style="font-size:0.68rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.12em;font-weight:900;">
            Forecast Status
        </div>
        <div style="margin-top:0.72rem;font-size:0.84rem;color:#E2E8F0;">
            <span class="status-dot"></span>Production predictions online
        </div>
        <div style="margin-top:0.5rem;font-size:0.72rem;color:#64748B;">
            {escape(city)} · {escape(str(run_date))}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Load ──────────────────────────────────────────────────────────────────────
with st.spinner("Loading predictions..."):
    pred_df = load_predictions(model_key, city, run_date)

if pred_df.empty:
    st.warning("No predictions found.")
    st.stop()

pred_df["forecast_timestamp"] = pd.to_datetime(pred_df["forecast_timestamp"])
pred_df = pred_df.sort_values("horizon_hours").reset_index(drop=True)

# ── Header ────────────────────────────────────────────────────────────────────
# champion_badge is new thing, also is line 162, 164, 165
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "india_map.png")
map_b64 = get_base64_image(img_path)
if map_b64:
    hero_img_html = f'<img src="data:image/png;base64,{map_b64}" style="width:100%; max-width:260px; filter: drop-shadow(0 0 20px rgba(157,78,221,0.5)); animation: float 6s ease-in-out infinite;">'
else:
    hero_img_html = '<div class="weather-glyph">🔮</div>'

hero_city = escape(str(city))
hero_run_date = escape(str(run_date))
hero_model = escape(str(sel_model["label"]))
champion_pill_html = '\n                <span class="meta-pill champion">👑 Champion Model</span>' if sel_model.get("is_champion") else ""
st.markdown(f"""
<section class="forecast-hero">
    <div class="hero-grid">
        <div>
            <div class="hero-kicker">Production Weather Intelligence</div>
            <h1 class="hero-title"><span>72-Hour</span><br>Forecast</h1>
            <div class="hero-line"></div>
            <div class="hero-copy">
                High-resolution operational forecast for {hero_city}, generated from the deployed model pipeline
                with 72 hourly prediction points across core weather signals.
            </div>
            <div class="meta-pills">
                <span class="meta-pill">📍 {hero_city}</span>
                <span class="meta-pill">🗓️ Generated {hero_run_date}</span>
                <span class="meta-pill">🧠 {hero_model}</span>{champion_pill_html}
                <span class="meta-pill">✅ Production Ready</span>
            </div>
        </div>
        <div class="hero-side">
            {hero_img_html}
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# ── Section 1: Next hour cards ────────────────────────────────────────────────
st.markdown("""
<div class="section-heading">
    <div>
        <div class="section-eyebrow">Next prediction window</div>
        <div class="section-title">Next Hour Conditions</div>
    </div>
    <div class="meta-pill">🕐 Horizon +1h</div>
</div>
""", unsafe_allow_html=True)

# horizon_hours=1 is the first predicted hour — matches leftmost graph point
next_hour = pred_df[pred_df["horizon_hours"] == 1].iloc[0]

card_configs = [
    ("temperature_2m",      "#FF4D8D", "°C", "Thermal index"),
    ("windspeed_10m",       "#00C8FF", "km/h", "Flow speed"),
    ("relativehumidity_2m", "#00F5A0", "%", "Moisture"),
    ("cloudcover",          "#9D4EDD", "%", "Sky coverage"),
    ("precipitation",       "#5B7CFA", "mm", "Rain signal"),
]

def metric_card_html(target: str, accent: str, unit: str, chip: str, feature: bool = False) -> str:
    val = next_hour[f"pred_{target}"]
    icon = TARGET_ICONS[target]
    lbl = TARGET_LABELS[target].split(" (")[0]
    feature_cls = " feature" if feature else ""
    return f"""
    <div class="metric-card{feature_cls}" style="--accent:{accent};">
        <div class="metric-top">
            <div class="metric-icon">{icon}</div>
            <div class="metric-chip">{escape(chip)}</div>
        </div>
        <div class="metric-label">{escape(lbl)}</div>
        <div class="metric-value" style="color:{accent};">{val:.1f}</div>
        <div class="metric-unit">{escape(unit)}</div>
    </div>
    """

feature_col, grid_col = st.columns([1.15, 1.85], gap="large")
with feature_col:
    target, accent, unit, chip = card_configs[0]
    st.markdown(metric_card_html(target, accent, unit, chip, feature=True), unsafe_allow_html=True)

with grid_col:
    top_left, top_right = st.columns(2)
    bottom_left, bottom_right = st.columns(2)
    for col, (target, accent, unit, chip) in zip(
        [top_left, top_right, bottom_left, bottom_right],
        card_configs[1:],
    ):
        with col:
            st.markdown(metric_card_html(target, accent, unit, chip), unsafe_allow_html=True)



st.markdown("---")

# ── Section 2: Day selector ───────────────────────────────────────────────────
st.markdown("#### 📅 Select Day")

run_dt    = pd.to_datetime(run_date)
day_dates = [run_dt + timedelta(days=i) for i in range(0, 3)]
day_labels = [
    f"Today · {day_dates[0].strftime('%b %d')}",
    f"Tomorrow · {day_dates[1].strftime('%b %d')}",
    f"{day_dates[2].strftime('%A')} · {day_dates[2].strftime('%b %d')}",
]

if "selected_day" not in st.session_state:
    st.session_state.selected_day = 0

def day_summary(df, day_dt):
    mask = df["forecast_timestamp"].dt.date == day_dt.date()
    sub  = df[mask]
    if sub.empty: return None
    return {
        "high"      : sub["pred_temperature_2m"].max(),
        "low"       : sub["pred_temperature_2m"].min(),
        "cloud"     : sub["pred_cloudcover"].mean(),
        "precip"    : sub["pred_precipitation"].sum(),     # total for display
        "precip_max": sub["pred_precipitation"].max(),     # max hourly for rain icon
    }

dc1, dc2, dc3 = st.columns(3)
for i, (dcol, label, day_dt) in enumerate(zip([dc1, dc2, dc3], day_labels, day_dates)):
    summary   = day_summary(pred_df, day_dt)
    is_active = (st.session_state.selected_day == i)
    card_cls  = "active" if is_active else "inactive"
    
    # Use the max hourly precipitation (not the daily sum) so the rain icon
    # only appears when at least one hour actually exceeds the 0.1 mm threshold
    emoji     = weather_emoji(
        summary["cloud"] if summary else 50, 
        summary["precip_max"] if summary else 0
    )

    with dcol:
        st.markdown(f"""
        <div class="day-card {card_cls}">
            <div style="font-size:0.95rem;font-weight:700;color:#ffffff;
                        text-transform:uppercase;letter-spacing:0.06em;">{label}</div>
            <div style="font-size:2.2rem;margin:0.4rem 0;">{emoji}</div>
            <div style="font-size:1.1rem;font-weight:700;color:#FFFFFF;">
                {f"{summary['high']:.0f}°" if summary else "—"}
                <span style="color:#212127;font-size:0.85rem;font-weight:400;">
                / {f"{summary['low']:.0f}°" if summary else "—"}
                </span>
            </div>
            <div style="font-size:0.72rem;color:#212127;margin-top:0.3rem;">
                {f"🌧️ {summary['precip']:.1f} mm" if summary else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "▶ View" if not is_active else "✓ Viewing",
            key=f"day_btn_{i}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.selected_day = i
            st.rerun()

# ── Filter to selected day ────────────────────────────────────────────────────
selected_day_dt = day_dates[st.session_state.selected_day]
day_mask        = pred_df["forecast_timestamp"].dt.date == selected_day_dt.date()
day_df          = pred_df[day_mask].copy()

if day_df.empty:
    st.warning("No predictions for this day.")
    st.stop()

st.markdown("---")

# ── Section 3: Cloud emoji row + Temperature chart ────────────────────────────
st.markdown(f"#### ☁️ Cloud cover")
st.markdown("<div style='font-size:0.75rem; color:#94A3B8; margin-bottom: 0.8rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Hover each icon for details</div>", unsafe_allow_html=True)

# Combine emoji and time into a single scrollable container
items_html = ""
for _, row in day_df.iterrows():
    hour   = row["forecast_timestamp"].strftime("%H")
    hour_int = int(hour)
    precip = row["pred_precipitation"]
    emoji  = weather_emoji(row["pred_cloudcover"], precip, hour_int)
    cloud_pct_str = f'{row["pred_cloudcover"]:.0f}'
    
    # Kept on a single line to prevent Markdown code block rendering
    items_html += f'<div style="flex: 1 0 2.8rem; text-align:center;"><div style="font-size:0.75rem; font-weight:800; color:#FFFFFF; margin-bottom:0.1rem;">{cloud_pct_str}%</div><div title="{hour}:00 · {cloud_pct_str}% clouds · {precip:.1f} mm rain" style="font-size:1.4rem; margin-bottom:0.1rem; filter: drop-shadow(0 0 8px rgba(255,255,255,0.15));">{emoji}</div><div style="font-size:0.7rem; font-weight:700; color:#94A3B8;">{hour}</div></div>'

st.markdown(f"""
<div style="
    position: relative;
    padding: 1.2rem 1rem 0.8rem;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(15,23,42,0.8), rgba(8,13,31,0.7)) padding-box,
                linear-gradient(135deg, rgba(0,200,255,0.5), rgba(157,78,221,0.4), rgba(255,77,141,0.3)) border-box;
    border: 1px solid transparent;
    box-shadow: 0 16px 32px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 2rem;
    backdrop-filter: blur(16px);
">
    <div style="display: flex; justify-content: space-between; overflow-x: auto; padding-bottom: 0.4rem; min-width: 100%; gap: 0.5rem;">
        {items_html}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"#### 🌡️ Temperature — {day_labels[st.session_state.selected_day]}")
temp_fig = make_chart(day_df, "temperature_2m", "#FF4D8D", height=300)
st.plotly_chart(temp_fig, use_container_width=True)

# ── Section 4: Other variables ────────────────────────────────────────────────
st.markdown("#### 📊 Other Variables")

other_map = {
    "💨 Wind Speed (km/h)"  : ("windspeed_10m",       "#457B9D"),
    "💧 Humidity (%)"       : ("relativehumidity_2m",  "#2A9D8F"),
    "🌧️ Precipitation (mm)" : ("precipitation",        "#1D3557"),
}

sel_label  = st.selectbox("Variable", list(other_map.keys()),
                           label_visibility="collapsed")
sel_target, sel_color = other_map[sel_label]
other_fig  = make_chart(day_df, sel_target, sel_color, height=280)
st.plotly_chart(other_fig, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
with st.expander("📄 Raw prediction data for selected day"):
    display_cols = ["forecast_timestamp", "horizon_hours"] + \
                   [f"pred_{t}" for t in TARGET_LABELS.keys()]
    display_cols = [c for c in display_cols if c in day_df.columns]
    st.dataframe(
        day_df[display_cols].rename(columns={f"pred_{t}": TARGET_LABELS[t] for t in TARGET_LABELS}),
        use_container_width=True, height=250,
    )
