# pages/2_Performance.py

import streamlit as st
import pandas as pd

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import get_available_models, TARGET_LABELS, TARGET_ICONS, champion_label
from utils.charts import mae_comparison_chart, multi_model_horizon_chart, rmse_heatmap, build_rmse_heatmap_html

st.set_page_config(page_title="Performance — Weather India", page_icon="📊", layout="wide")

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

/* Hide default Streamlit page navigation (fixes duplicate sidebar) */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Sidebar */
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
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: rgba(203,213,225,0.7) !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}
[data-testid="stSidebar"] hr { border-color: rgba(0,200,255,0.16) !important; }

/* Performance card — dark glassmorphism */
.perf-card {
    background: linear-gradient(180deg, rgba(15,23,42,0.82), rgba(8,13,31,0.70)) padding-box,
                linear-gradient(135deg, rgba(0,200,255,0.4), rgba(255,255,255,0.10), rgba(157,78,221,0.28)) border-box;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid transparent;
    border-radius: 22px;
    padding: 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 18px 42px rgba(0,0,0,0.26);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.perf-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 24px 58px rgba(0,0,0,0.34), 0 0 34px rgba(0,200,255,0.18);
}

/* Hide defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header[data-testid="stHeader"] {
    background: rgba(3,7,18,0.72);
    backdrop-filter: blur(12px);
}
hr { border-color: rgba(0,200,255,0.10) !important; margin: 1.75rem 0 !important; }

/* ── Badge-style buttons for heatmap controls ───────────────── */
[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, rgba(15,23,42,0.90), rgba(8,13,31,0.80)) padding-box,
                linear-gradient(135deg, rgba(0,200,255,0.30), rgba(157,78,221,0.22)) border-box !important;
    border: 1.5px solid transparent !important;
    border-radius: 999px !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 200ms ease !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(0,200,255,0.12) !important;
    color: #CBD5E1 !important;
}
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(15,23,42,0.90), rgba(8,13,31,0.80)) padding-box,
                linear-gradient(135deg, rgba(0,200,255,0.60), rgba(157,78,221,0.55), rgba(255,77,141,0.40)) border-box !important;
    border: 1.5px solid transparent !important;
    border-radius: 999px !important;
    color: #E2E8F0 !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    box-shadow: 0 2px 14px rgba(0,200,255,0.14), 0 0 10px rgba(157,78,221,0.08) !important;
    transition: all 200ms ease !important;
}
[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(0,200,255,0.22), 0 0 18px rgba(157,78,221,0.14) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #030712; }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.35); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(157,78,221,0.55); }

/* ── Gradient-outline info badges ───────────────────────────── */
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    align-items: center;
    margin-top: 1rem;
}
.info-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.38rem 1rem;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    color: #CBD5E1;
    border-radius: 999px;
    background:
        linear-gradient(135deg, rgba(15,23,42,0.90), rgba(8,13,31,0.80)) padding-box,
        linear-gradient(135deg, rgba(0,200,255,0.50), rgba(157,78,221,0.45), rgba(255,77,141,0.35)) border-box;
    border: 1.5px solid transparent;
    box-shadow: 0 2px 12px rgba(0,0,0,0.22), 0 0 8px rgba(0,200,255,0.08);
    transition: transform 200ms ease, box-shadow 200ms ease;
    white-space: nowrap;
}
.info-badge:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 6px 20px rgba(0,0,0,0.30), 0 0 18px rgba(0,200,255,0.18);
}
.info-badge.champion {
    background:
        linear-gradient(135deg, rgba(30,20,8,0.92), rgba(20,14,4,0.82)) padding-box,
        linear-gradient(135deg, #FFD700, #FFAA00, #FF8C00) border-box;
    border: 1.5px solid transparent;
    color: #FFD700;
    box-shadow: 0 2px 14px rgba(255,215,0,0.18), 0 0 10px rgba(255,170,0,0.10);
}
.model-name-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.55rem 1.5rem;
    font-size: 1.05rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    color: #FFFFFF;
    letter-spacing: 0.02em;
    border-radius: 999px;
    background:
        linear-gradient(135deg, rgba(15,23,42,0.88), rgba(8,13,31,0.78)) padding-box,
        linear-gradient(135deg, #00C8FF, #9D4EDD, #FF4D8D) border-box;
    border: 2px solid transparent;
    box-shadow: 0 4px 22px rgba(0,200,255,0.16), 0 0 28px rgba(157,78,221,0.10);
    transition: transform 220ms ease, box-shadow 220ms ease;
}
.model-name-badge:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 8px 32px rgba(0,200,255,0.24), 0 0 36px rgba(157,78,221,0.18);
}

/* Hero and typography styles */
@keyframes fade-up {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%, 100% { opacity: 0.72; filter: saturate(1); }
    50% { opacity: 1; filter: saturate(1.5); }
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
    grid-template-columns: minmax(0, 1fr) minmax(280px, 0.6fr);
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
.hero-title > span:first-child {
    background: linear-gradient(110deg, #00C8FF 0%, #9D4EDD 52%, #FF4D8D 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 18px rgba(0,200,255,0.20));
}
.hero-title .model-name-badge {
    -webkit-text-fill-color: #FFFFFF !important;
    color: #FFFFFF !important;
    filter: none !important;
    font-size: 0.45em;
    padding: 0.35em 0.9em;
    vertical-align: middle;
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
</style>
""", unsafe_allow_html=True)



with st.spinner("Loading model metrics..."):
    models = get_available_models()

if not models:
    st.error("No Production models found.")
    st.stop()

# ── Model selector in sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 0.6rem;">
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
    # original line was : model_labels = [m["label"] for m in models]
    model_labels = [champion_label(m) for m in models]
    selected_idx = st.selectbox("Focus model", range(len(model_labels)),
                                 format_func=lambda i: model_labels[i])

selected_model = models[selected_idx]

# ── Dashboard Banner & KPI Row ────────────────────────────────────────────────
cfg = selected_model["config"]
arch = cfg.get("architecture", "GRU Encoder Decoder")
cities = cfg.get("cities", 7)
horizon = cfg.get("output_len", 72)
test_year_raw = cfg.get("test_year", "unknown")
# Strip brackets if present, e.g. "[2021]" → "2021"
test_year = str(test_year_raw).strip("[]").strip()
val_loss = selected_model["val_metrics"].get("best_val_loss")

all_rmses = [m["rmse"] for m in selected_model["test_metrics"].values() if m.get("rmse") is not None]
avg_rmse = sum(all_rmses) / len(all_rmses) if all_rmses else 0

all_maes = [m["mae"] for m in selected_model["test_metrics"].values() if m.get("mae") is not None]
avg_mae = sum(all_maes) / len(all_maes) if all_maes else 0

overall_score = f"{(1 - val_loss)*100:.1f}/100" if val_loss is not None else "—"
model_label = selected_model.get("label", "Unknown Model")

# Build badge list dynamically — avoids empty lines that break Streamlit HTML
badges = []
if selected_model.get("is_champion"):
    badges.append('<span class="info-badge champion">👑 Champion</span>')
# badges.append(f'<span class="model-name-badge">🧠 {arch}</span>')
badges.append(f'<span class="info-badge">🧠 {arch}</span>')
badges.append(f'<span class="info-badge">🗓️ {test_year} Test Set</span>')
badges.append(f'<span class="info-badge">⏱️ {horizon}-Hour Forecast</span>')
badges.append(f'<span class="info-badge">📍 {cities} Cities</span>')
badges_html = "\n        ".join(badges)

st.markdown(f"""<section class="forecast-hero" style="min-height: 140px; padding: 1.6rem 2rem; margin-bottom: 1.5rem; display: flex; flex-direction: column; justify-content: center; align-items: center;">
    <div style="text-align: center; width: 100%;">
        <h1 class="hero-title" style="font-size: 2.2rem; margin-top: 0; display: inline-flex; align-items: center; flex-wrap: wrap; justify-content: center; gap: 0.4rem;"><span>Model</span> Performance <span style="font-size: 0.50em; font-weight: 500; color: #94A3B8 !important; -webkit-text-fill-color: #94A3B8 !important; letter-spacing: 0.01em;"> </span> <span class="model-name-badge" style="-webkit-text-fill-color: #FFFFFF !important; color: #FFFFFF !important; background: linear-gradient(135deg, rgba(15,23,42,0.88), rgba(8,13,31,0.78)) padding-box, linear-gradient(135deg, #00C8FF, #9D4EDD, #FF4D8D) border-box !important; border: 2px solid transparent;">{model_label}</span></h1>
    </div>
    <div class="badge-row" style="margin-top: 1.1rem; justify-content: center;">
        {badges_html}
    </div>
</section>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.2rem; margin-bottom: 2.5rem;">
    <div class="perf-card" style="margin-bottom:0; text-align:center; padding: 1.2rem;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em; font-weight: 700;">Overall Score</div>
        <div style="font-size:2.2rem; font-weight:800; color:#00F5A0; font-family:'Space Grotesk',sans-serif; text-shadow:0 0 16px rgba(0,245,160,0.3); margin-top:0.4rem;">{overall_score}</div>
    </div>
    <div class="perf-card" style="margin-bottom:0; text-align:center; padding: 1.2rem;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em; font-weight: 700;">Best Val Loss</div>
        <div style="font-size:2.2rem; font-weight:800; color:#00C8FF; font-family:'Space Grotesk',sans-serif; text-shadow:0 0 16px rgba(0,200,255,0.3); margin-top:0.4rem;">{f"{val_loss:.4f}" if val_loss is not None else "—"}</div>
    </div>
    <div class="perf-card" style="margin-bottom:0; text-align:center; padding: 1.2rem;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em; font-weight: 700;">Avg RMSE</div>
        <div style="font-size:2.2rem; font-weight:800; color:#9D4EDD; font-family:'Space Grotesk',sans-serif; text-shadow:0 0 16px rgba(157,78,221,0.3); margin-top:0.4rem;">{avg_rmse:.3f}</div>
    </div>
    <div class="perf-card" style="margin-bottom:0; text-align:center; padding: 1.2rem;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em; font-weight: 700;">Avg MAE</div>
        <div style="font-size:2.2rem; font-weight:800; color:#FF4D8D; font-family:'Space Grotesk',sans-serif; text-shadow:0 0 16px rgba(255,77,141,0.3); margin-top:0.4rem;">{avg_mae:.3f}</div>
    </div>
    <div class="perf-card" style="margin-bottom:0; text-align:center; padding: 1.2rem;">
        <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em; font-weight: 700;">Forecast Horizon</div>
        <div style="font-size:2.2rem; font-weight:800; color:#FFB547; font-family:'Space Grotesk',sans-serif; text-shadow:0 0 16px rgba(255,181,71,0.3); margin-top:0.4rem;">{horizon}h</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Test metrics table ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"### 🎯 Test Set Results — {test_year}")

test_cols = st.columns(5)
for i, target in enumerate(TARGET_LABELS.keys()):
    tm    = selected_model["test_metrics"][target]
    icon  = TARGET_ICONS[target]
    label = TARGET_LABELS[target].split(" (")[0]
    unit  = TARGET_LABELS[target].split("(")[-1].rstrip(")")
    mae   = f"{tm['mae']:.3f}"  if tm.get("mae")  is not None else "—"
    rmse  = f"{tm['rmse']:.3f}" if tm.get("rmse") is not None else "—"
    with test_cols[i]:
        st.markdown(f"""
        <div class="perf-card" style="text-align:center;">
            <div style="font-size:1.3rem;">{icon}</div>
            <div style="font-size:0.72rem;color:#64748B;text-transform:uppercase;
                        letter-spacing:0.04em;margin:0.2rem 0;">{label}</div>
            <div style="margin-top:0.5rem;">
                <span style="font-size:0.7rem;color:#64748B;">MAE</span><br>
                <span style="font-size:1.3rem;font-weight:700;color:#60A5FA;
                             font-family:'Space Grotesk',sans-serif;">
                    {mae}
                </span>
                <span style="font-size:0.7rem;color:#64748B;"> {unit}</span>
            </div>
            <div style="margin-top:0.4rem;">
                <span style="font-size:0.7rem;color:#64748B;">RMSE</span><br>
                <span style="font-size:1.1rem;font-weight:600;color:#CBD5E1;">
                    {rmse}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Horizon degradation — multi-model comparison ─────────────────────────────
st.markdown("---")
st.markdown("### 📉 MAE Degradation by Forecast Horizon")
st.markdown("<p style='color:#94A3B8;'>Compare how prediction accuracy degrades from 6h to 72h across all models.</p>", unsafe_allow_html=True)

target_options = list(TARGET_LABELS.keys())
target_display = {t: f"{TARGET_ICONS[t]}  {TARGET_LABELS[t]}" for t in target_options}

ctrl_col, chart_col = st.columns([1, 3], gap="large")

with ctrl_col:
    st.markdown("<div style='font-size:0.75rem; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:0.4rem;'>Feature</div>", unsafe_allow_html=True)
    selected_target = st.selectbox(
        "Feature",
        target_options,
        format_func=lambda t: target_display[t],
        label_visibility="collapsed",
    )

    st.markdown("<div style='font-size:0.75rem; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-top:1.2rem; margin-bottom:0.4rem;'>Models</div>", unsafe_allow_html=True)

    active_keys = set()
    for mdl in models:
        is_champ = mdl.get("is_champion", False)
        cb_label = f"👑 {mdl['label']}" if is_champ else mdl["label"]
        checked  = st.checkbox(cb_label, value=True, key=f"hz_{mdl['model_key']}")
        if checked:
            active_keys.add(mdl["model_key"])

with chart_col:
    fig = multi_model_horizon_chart(models, selected_target, active_keys)
    st.plotly_chart(fig, use_container_width=True)

# ── Multi-model comparison (if more than 1 model) ────────────────────────────
if len(models) > 1:
    st.markdown("---")
    st.markdown("### Model RMSE Comparison")

    # ── Session state for sort ────────────────────────────────────────────
    if "hm_sort_target" not in st.session_state:
        st.session_state.hm_sort_target = None
    if "hm_sort_dir" not in st.session_state:
        st.session_state.hm_sort_dir = None
    if "hm_scale" not in st.session_state:
        st.session_state.hm_scale = "per_metric"

    # ── Scale mode badges ─────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.75rem; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:0.3rem;'>Color scale</div>", unsafe_allow_html=True)
    sc1, sc2, sc_spacer = st.columns([1, 1, 4])
    with sc1:
        if st.button(
            "Per metric",
            key="btn_scale_pm",
            type="primary" if st.session_state.hm_scale == "per_metric" else "secondary",
            use_container_width=True,
        ):
            st.session_state.hm_scale = "per_metric"
            st.rerun()
    with sc2:
        if st.button(
            "Global scale",
            key="btn_scale_gl",
            type="primary" if st.session_state.hm_scale == "global" else "secondary",
            use_container_width=True,
        ):
            st.session_state.hm_scale = "global"
            st.rerun()

    # ── Sort buttons (feature labels as toggles) ─────────────────────────
    st.markdown("<div style='font-size:0.75rem; color:#64748B; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-top:0.8rem; margin-bottom:0.3rem;'>Sort by metric <span style=\"font-size:0.68rem; font-weight:400; font-style:italic;\">(click to toggle)</span></div>", unsafe_allow_html=True)
    sort_cols = st.columns(len(TARGET_LABELS))
    for i, t_key in enumerate(TARGET_LABELS):
        with sort_cols[i]:
            is_sorted = st.session_state.hm_sort_target == t_key
            if is_sorted:
                arrow = " ↑" if st.session_state.hm_sort_dir == "asc" else " ↓"
            else:
                arrow = ""
            short_name = TARGET_LABELS[t_key].split(" (")[0]
            btn_label = f"{TARGET_ICONS[t_key]} {short_name}{arrow}"
            btn_type = "primary" if is_sorted else "secondary"
            if st.button(btn_label, key=f"sort_{t_key}", type=btn_type, use_container_width=True):
                if is_sorted:
                    if st.session_state.hm_sort_dir == "asc":
                        st.session_state.hm_sort_dir = "desc"
                    else:
                        st.session_state.hm_sort_target = None
                        st.session_state.hm_sort_dir = None
                else:
                    st.session_state.hm_sort_target = t_key
                    st.session_state.hm_sort_dir = "asc"
                st.rerun()

    # ── Heatmap HTML table ────────────────────────────────────────────────
    heatmap_html = build_rmse_heatmap_html(
        models,
        scale_mode=st.session_state.hm_scale,
        sort_target=st.session_state.hm_sort_target,
        sort_dir=st.session_state.hm_sort_dir,
    )
    st.markdown(heatmap_html, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### MAE vs RMSE per Target")
    mae_cols = st.columns(3)
    for i, target in enumerate(TARGET_LABELS.keys()):
        with mae_cols[i % 3]:
            fig = mae_comparison_chart(models, target)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown("---")
    st.info("Train and register additional models to enable model comparison charts.")