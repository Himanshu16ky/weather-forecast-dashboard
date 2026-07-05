# utils/charts.py
# All chart building logic using Plotly

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.data_loader import TARGET_LABELS, TARGET_COLORS, TARGET_ICONS

FONT_FAMILY = "Inter, 'Space Grotesk', sans-serif"
GRID_COLOR  = "rgba(255,255,255,0.08)"
BG_COLOR    = "#0A1628"
PAPER_COLOR = "#0A1628"


def base_layout(title: str = "", height: int = 400) -> dict:
    return dict(
        title=dict(text=title, font=dict(family=FONT_FAMILY, size=16, color="#E2E8F0")),
        height=height,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=PAPER_COLOR,
        font=dict(family=FONT_FAMILY, color="#CBD5E1"),
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False),
        legend=dict(bgcolor="rgba(10,22,40,0.8)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1, font=dict(color="#CBD5E1")),
        margin=dict(l=50, r=20, t=50, b=40),
        hovermode="x unified",
    )


def forecast_chart(df: pd.DataFrame, target: str, city: str) -> go.Figure:
    """72h forecast line chart for a single target."""
    label = TARGET_LABELS[target]
    color = TARGET_COLORS[target]
    icon  = TARGET_ICONS[target]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["forecast_timestamp"],
        y=df[f"pred_{target}"],
        mode="lines",
        name=label,
        line=dict(color=color, width=2.5),
        fill="tozeroy",
        fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba") if "rgb" in color else color + "15",
        hovertemplate=f"<b>%{{x|%a %b %d, %H:%M}}</b><br>{icon} {label}: %{{y:.1f}}<extra></extra>",
    ))

    # Mark day boundaries
    for ts in df["forecast_timestamp"]:
        if ts.hour == 0:
            fig.add_vline(x=ts, line_dash="dot", line_color="rgba(255,255,255,0.15)", line_width=1.5)

    layout = base_layout(f"{icon} {label} — {city}", height=280)
    layout["yaxis"]["title"] = label
    fig.update_layout(**layout)
    return fig


def all_forecasts_chart(df: pd.DataFrame, city: str) -> go.Figure:
    """Combined 72h forecast chart with all 5 targets on subplots."""
    targets = list(TARGET_LABELS.keys())
    fig     = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        subplot_titles=[f"{TARGET_ICONS[t]} {TARGET_LABELS[t]}" for t in targets],
        vertical_spacing=0.06,
    )

    for i, target in enumerate(targets, 1):
        color = TARGET_COLORS[target]
        fig.add_trace(
            go.Scatter(
                x=df["forecast_timestamp"],
                y=df[f"pred_{target}"],
                mode="lines",
                name=TARGET_LABELS[target],
                line=dict(color=color, width=2),
                showlegend=False,
                hovertemplate=f"%{{y:.1f}}<extra>{TARGET_LABELS[target]}</extra>",
            ),
            row=i, col=1
        )
        fig.update_yaxes(gridcolor=GRID_COLOR, row=i, col=1)
        fig.update_xaxes(gridcolor=GRID_COLOR, row=i, col=1)

    fig.update_layout(
        height=900,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=PAPER_COLOR,
        font=dict(family=FONT_FAMILY, color="#CBD5E1"),
        margin=dict(l=60, r=20, t=30, b=40),
        hovermode="x unified",
        title=dict(
            text=f"72-Hour Forecast — {city}",
            font=dict(family=FONT_FAMILY, size=18, color="#E2E8F0")
        ),
    )
    return fig


def mae_comparison_chart(models_data: list[dict], target: str) -> go.Figure:
    """Grouped bar chart comparing MAE and RMSE across models for a single target."""
    mae_color = TARGET_COLORS[target]

    # Per-target contrasting RMSE colors (each distinct from the MAE color for that target)
    _RMSE_COLORS = {
        "temperature_2m":      "#00C8FF",  # cyan   vs red MAE
        "windspeed_10m":       "#FF4D8D",  # pink   vs blue MAE
        "relativehumidity_2m": "#FFB547",  # amber  vs teal MAE
        "cloudcover":          "#9D4EDD",  # purple vs grey-blue MAE
        "precipitation":       "#00F5A0",  # green  vs navy MAE
    }
    rmse_color = _RMSE_COLORS.get(target, "#00C8FF")

    # Safely extract labels, MAE, and RMSE — skip models missing this target
    labels, maes, rmses = [], [], []
    for m in models_data:
        t_metrics = m.get("test_metrics", {}).get(target, {})
        mae_val  = t_metrics.get("mae")
        rmse_val = t_metrics.get("rmse")
        if mae_val is None and rmse_val is None:
            continue  # skip models with no data for this target
        labels.append(m["label"])
        maes.append(mae_val if mae_val is not None else 0)
        rmses.append(rmse_val if rmse_val is not None else 0)

    fig = go.Figure()

    if not labels:
        # No data at all — return an empty styled figure with a message
        layout = base_layout(
            f"{TARGET_ICONS[target]} {TARGET_LABELS[target]} — MAE vs RMSE",
            height=380,
        )
        fig.update_layout(**layout)
        fig.add_annotation(
            text="No metric data available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#94A3B8", family=FONT_FAMILY),
        )
        return fig

    # MAE bars
    fig.add_trace(go.Bar(
        x=labels,
        y=maes,
        name="MAE",
        marker_color=mae_color,
        marker_line_color="rgba(255,255,255,0.15)",
        marker_line_width=0.5,
        text=[f"{v:.3f}" for v in maes],
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="#FFFFFF", size=11, family=FONT_FAMILY),
        hovertemplate="MAE: %{y:.3f}<extra></extra>",
    ))

    # RMSE bars
    fig.add_trace(go.Bar(
        x=labels,
        y=rmses,
        name="RMSE",
        marker_color=rmse_color,
        marker_line_color="rgba(255,255,255,0.10)",
        marker_line_width=0.5,
        text=[f"{v:.3f}" for v in rmses],
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="#FFFFFF", size=11, family=FONT_FAMILY),
        hovertemplate="RMSE: %{y:.3f}<extra></extra>",
    ))

    layout = base_layout(
        f"{TARGET_ICONS[target]} {TARGET_LABELS[target]} — MAE vs RMSE",
        height=380,
    )
    layout["yaxis"]["title"] = TARGET_LABELS[target]
    layout["barmode"]        = "group"
    layout["bargap"]         = 0.25
    layout["bargroupgap"]    = 0.06
    layout["title"]["x"] = 0.02
    layout["title"]["xanchor"] = "left"
    layout["title"]["y"] = 0.95
    layout["title"]["yanchor"] = "top"

    layout["legend"] = dict(
        bgcolor="rgba(10,22,40,0.85)",
        bordercolor="rgba(255,255,255,0.10)",
        borderwidth=1,
        font=dict(color="#CBD5E1", size=11),
        orientation="h",
        yanchor="bottom",   # was "top"
        y=1.1,              # was 0.99 — this was the bug: 0.99 sits just inside
                             # the plot area (near the tallest bars); anything
                             # above 1.0 sits safely in the top margin instead
        xanchor="right",
        x=0.99,
    )
    layout["xaxis"]["tickangle"] = -30 if len(labels) > 4 else 0
    layout["xaxis"]["tickfont"]  = dict(size=10, color="#CBD5E1")
    layout["margin"]["t"]        = 78   # was 70 — small bump back up to give the legend room
    layout["margin"]["b"]        = 70
    fig.update_layout(**layout)
    return fig


def horizon_degradation_chart(model_data: dict, target: str) -> go.Figure:
    """Line chart showing MAE degradation across forecast horizons."""
    horizons = [6, 24, 48, 72]
    h_data   = model_data["horizon_metrics"][target]
    maes     = [h_data.get(f"h{h}") for h in horizons]

    if any(v is None for v in maes):
        return None

    color = TARGET_COLORS[target]
    fig   = go.Figure()
    fig.add_trace(go.Scatter(
        x=horizons,
        y=maes,
        mode="lines+markers",
        name=TARGET_LABELS[target],
        line=dict(color=color, width=2.5),
        marker=dict(size=8, color=color, line=dict(color="#0A1628", width=2)),
        hovertemplate="<b>%{x} </b><br>MAE: %{y:.3f}<extra></extra>",
    ))

    layout = base_layout(
        f"{TARGET_ICONS[target]} MAE vs Horizon",
        height=280
    )
    layout["xaxis"]["title"]      = "Forecast Horizon (hours)"
    layout["xaxis"]["tickvals"]   = horizons
    layout["xaxis"]["ticktext"]   = [f"{h}h" for h in horizons]
    layout["yaxis"]["title"]      = "MAE"
    fig.update_layout(**layout)
    return fig


# ── Curated color palette for multi-model charts ─────────────────────────────
MODEL_COLORS = [
    "#00C8FF",  # cyan
    "#FF4D8D",  # pink
    "#00F5A0",  # green
    "#FFB547",  # amber
    "#9D4EDD",  # purple
    "#FF6B35",  # orange
    "#4ECDC4",  # teal
    "#F7DC6F",  # gold
    "#E74C3C",  # red
    "#3498DB",  # blue
]

GREY_INACTIVE = "#3E4C5E"


def multi_model_horizon_chart(
    models_data: list[dict],
    target: str,
    active_model_keys: set[str],
) -> go.Figure:
    """
    Single chart comparing MAE degradation across forecast horizons
    for ALL models.  Active models are colored; inactive are greyed out.
    """
    horizons   = [6, 24, 48, 72]
    tick_texts = [f"{h}h" for h in horizons]
    label      = TARGET_LABELS[target]
    icon       = TARGET_ICONS[target]
    unit       = label.split("(")[-1].rstrip(")") if "(" in label else ""

    fig = go.Figure()

    # Draw inactive (greyed-out) traces first so they sit behind
    for i, model in enumerate(models_data):
        h_data = model.get("horizon_metrics", {}).get(target, {})
        maes   = [h_data.get(f"h{h}") for h in horizons]
        if any(v is None for v in maes):
            continue

        model_key   = model["model_key"]
        is_active   = model_key in active_model_keys
        is_champion = model.get("is_champion", False)
        display_name = f"👑 {model['label']}" if is_champion else model["label"]
        color       = MODEL_COLORS[i % len(MODEL_COLORS)]

        if not is_active:
            fig.add_trace(go.Scatter(
                x=horizons,
                y=maes,
                mode="lines",
                name=display_name,
                line=dict(color=GREY_INACTIVE, width=1.5, dash="dot"),
                opacity=0.4,
                hovertemplate=(
                    f"<b>{display_name}</b><br>"
                    f"MAE: %{{y:.3f}}"
                    f"<extra></extra>"
                ),
                legendgroup=model_key,
            ))

    # Draw active (colored) traces on top
    for i, model in enumerate(models_data):
        h_data = model.get("horizon_metrics", {}).get(target, {})
        maes   = [h_data.get(f"h{h}") for h in horizons]
        if any(v is None for v in maes):
            continue

        model_key   = model["model_key"]
        is_active   = model_key in active_model_keys
        is_champion = model.get("is_champion", False)
        display_name = f"👑 {model['label']}" if is_champion else model["label"]
        color       = MODEL_COLORS[i % len(MODEL_COLORS)]

        if is_active:
            line_width = 3.5 if is_champion else 2.5
            fig.add_trace(go.Scatter(
                x=horizons,
                y=maes,
                mode="lines+markers",
                name=display_name,
                line=dict(color=color, width=line_width),
                marker=dict(
                    size=9 if is_champion else 7,
                    color=color,
                    line=dict(color="#0A1628", width=2),
                ),
                hovertemplate=(
                    f"<b>{display_name}</b><br>"
                    f"MAE: %{{y:.3f}}"
                    f"<extra></extra>"
                ),
                legendgroup=model_key,
            ))

    y_title = f"MAE ({unit})" if unit else "MAE"
    layout  = base_layout(f"{icon} {label} — MAE vs Forecast Horizon", height=480)
    layout["xaxis"]["title"]    = "Forecast Horizon (hours)"
    layout["xaxis"]["tickvals"] = horizons
    layout["xaxis"]["ticktext"] = tick_texts
    layout["yaxis"]["title"]    = y_title
    layout["legend"] = dict(
        bgcolor="rgba(10,22,40,0.85)",
        bordercolor="rgba(255,255,255,0.12)",
        borderwidth=1,
        font=dict(color="#CBD5E1", size=12),
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
    )
    layout["margin"]["r"] = 160  # room for legend on the right
    fig.update_layout(**layout)
    return fig


def prediction_vs_actual_chart(
    pred_df: pd.DataFrame,
    actual_df: pd.DataFrame,
    target: str,
    city: str
) -> go.Figure:
    """Line chart overlaying predictions vs actual observed values."""
    label = TARGET_LABELS[target]
    color = TARGET_COLORS[target]
    icon  = TARGET_ICONS[target]

    fig = go.Figure()

    # Actual line
    fig.add_trace(go.Scatter(
        x=actual_df["timestamp"],
        y=actual_df[target],
        mode="lines",
        name="Actual (Open-Meteo)",
        line=dict(color="#E2E8F0", width=2, dash="solid"),
        hovertemplate=f"<b>Actual</b>: %{{y:.1f}}<extra></extra>",
    ))

    # Prediction line
    fig.add_trace(go.Scatter(
        x=pred_df["forecast_timestamp"],
        y=pred_df[f"pred_{target}"],
        mode="lines",
        name="Model Prediction",
        line=dict(color=color, width=2, dash="dash"),
        hovertemplate=f"<b>Predicted</b>: %{{y:.1f}}<extra></extra>",
    ))

    layout = base_layout(f"{icon} {label} — Predictions vs Actual | {city}", height=350)
    layout["yaxis"]["title"] = label
    fig.update_layout(**layout)
    return fig


def _interpolate_blue(t: float) -> str:
    """Interpolate from lightest blue (t=0, best) to darkest blue (t=1, worst)."""
    # #DBEAFE -> (219, 234, 254)  to  #1E3A5F -> (30, 58, 95)
    r = int(219 + (30 - 219) * t)
    g = int(234 + (58 - 234) * t)
    b = int(254 + (95 - 254) * t)
    return f"rgb({r},{g},{b})"


# Sequential single-hue blue: lightest = best, darkest = worst
_BLUE_SCALE = [
    [0.00, "#DBEAFE"],
    [0.25, "#93C5FD"],
    [0.50, "#3B82F6"],
    [0.75, "#1D4ED8"],
    [1.00, "#1E3A5F"],
]


def rmse_heatmap(
    models_data: list[dict],
    scale_mode: str = "per_metric",
    sort_config: tuple | None = None,
) -> go.Figure:
    """
    Advanced RMSE heatmap with:
    - Per-column or global normalization (scale_mode)
    - Row sorting by any target (sort_config)
    - Best-in-column green outline highlights
    - Hover showing true RMSE + rank
    - Custom gradient legend bar
    """
    targets      = list(TARGET_LABELS.keys())
    n_targets    = len(targets)
    col_labels   = [TARGET_LABELS[t] for t in targets]

    # ── 1. Build raw data + model labels ──────────────────────────────────────
    indices = list(range(len(models_data)))
    raw_z = [
        [models_data[i]["test_metrics"][t]["rmse"] for t in targets]
        for i in indices
    ]
    m_labels = [
        (f"👑 {models_data[i]['label']}" if models_data[i].get("is_champion") else models_data[i]["label"])
        for i in indices
    ]

    # ── 2. Sort rows ─────────────────────────────────────────────────────────
    if sort_config is not None:
        sort_target, sort_dir = sort_config
        col_idx = targets.index(sort_target)
        order = sorted(range(len(indices)), key=lambda r: raw_z[r][col_idx],
                        reverse=(sort_dir == "desc"))
        raw_z    = [raw_z[r] for r in order]
        m_labels = [m_labels[r] for r in order]

    n_models = len(m_labels)

    # ── 3. Rank per column (on raw values, 1 = best/lowest) ──────────────────
    ranks = [[0] * n_targets for _ in range(n_models)]
    for c in range(n_targets):
        col_vals = [(raw_z[r][c], r) for r in range(n_models)]
        col_vals.sort(key=lambda x: x[0])
        for rank_pos, (_, row) in enumerate(col_vals, 1):
            ranks[row][c] = rank_pos

    # ── 4. Find best (min) per column ────────────────────────────────────────
    best_rows = []
    for c in range(n_targets):
        col_vals = [raw_z[r][c] for r in range(n_models)]
        best_rows.append(col_vals.index(min(col_vals)))

    # ── 5. Normalize z ───────────────────────────────────────────────────────
    if scale_mode == "per_metric":
        norm_z = [[0.0] * n_targets for _ in range(n_models)]
        for c in range(n_targets):
            col_vals = [raw_z[r][c] for r in range(n_models)]
            c_min, c_max = min(col_vals), max(col_vals)
            c_range = c_max - c_min if c_max != c_min else 1.0
            for r in range(n_models):
                norm_z[r][c] = (raw_z[r][c] - c_min) / c_range
        scale_text = "Colors scaled: per metric"
    else:
        flat = [raw_z[r][c] for r in range(n_models) for c in range(n_targets)]
        g_min, g_max = min(flat), max(flat)
        g_range = g_max - g_min if g_max != g_min else 1.0
        norm_z = [
            [(raw_z[r][c] - g_min) / g_range for c in range(n_targets)]
            for r in range(n_models)
        ]
        scale_text = f"Colors scaled: {g_min:.2f}–{g_max:.2f} global"

    # ── 6. Customdata: [real_rmse, rank, total_models] ───────────────────────
    customdata = [
        [[raw_z[r][c], ranks[r][c], n_models] for c in range(n_targets)]
        for r in range(n_models)
    ]

    # ── 7. Cell text (real RMSE, 2 decimals) ─────────────────────────────────
    cell_text = [[f"{raw_z[r][c]:.2f}" for c in range(n_targets)] for r in range(n_models)]

    # ── 8. Build figure ──────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=norm_z,
        x=col_labels,
        y=m_labels,
        zmin=0,
        zmax=1,
        colorscale=_BLUE_SCALE,
        showscale=False,
        text=cell_text,
        texttemplate="%{text}",
        textfont=dict(color="#E2E8F0", size=13, family=FONT_FAMILY),
        customdata=customdata,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x}<br>"
            "RMSE: %{customdata[0]:.2f}<br>"
            "Rank: %{customdata[1]} of %{customdata[2]}"
            "<extra></extra>"
        ),
        xgap=3,
        ygap=3,
    ))

    # ── 9. Best-in-column highlight outlines ─────────────────────────────────
    for c, best_r in enumerate(best_rows):
        fig.add_shape(
            type="rect",
            x0=c - 0.5, x1=c + 0.5,
            y0=best_r - 0.5, y1=best_r + 0.5,
            xref="x", yref="y",
            line=dict(color="#00F5A0", width=2.5),
            fillcolor="rgba(0,0,0,0)",
        )

    # ── 10. Scale-mode annotation ────────────────────────────────────────────
    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.0, y=1.08,
        text=f"<i>{scale_text}</i>",
        showarrow=False,
        font=dict(size=11, color="#64748B", family=FONT_FAMILY),
        xanchor="right",
    )

    # ── 11. Custom gradient legend bar ───────────────────────────────────────
    n_steps = 30
    bar_y0, bar_y1 = -0.18, -0.13
    bar_x_start, bar_x_end = 0.25, 0.75
    step_w = (bar_x_end - bar_x_start) / n_steps

    for i in range(n_steps):
        t = i / (n_steps - 1)
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=bar_x_start + i * step_w,
            x1=bar_x_start + (i + 1) * step_w,
            y0=bar_y0, y1=bar_y1,
            fillcolor=_interpolate_blue(t),
            line=dict(width=0),
        )

    # Rounded end caps
    fig.add_shape(
        type="rect", xref="paper", yref="paper",
        x0=bar_x_start, x1=bar_x_start + step_w,
        y0=bar_y0, y1=bar_y1,
        fillcolor=_interpolate_blue(0),
        line=dict(width=0),
    )
    fig.add_shape(
        type="rect", xref="paper", yref="paper",
        x0=bar_x_end - step_w, x1=bar_x_end,
        y0=bar_y0, y1=bar_y1,
        fillcolor=_interpolate_blue(1),
        line=dict(width=0),
    )

    # Legend text labels
    fig.add_annotation(
        xref="paper", yref="paper",
        x=bar_x_start - 0.01,
        y=(bar_y0 + bar_y1) / 2,
        text="Lower RMSE<br>(better)",
        showarrow=False,
        xanchor="right",
        font=dict(size=10, color="#94A3B8", family=FONT_FAMILY),
    )
    fig.add_annotation(
        xref="paper", yref="paper",
        x=bar_x_end + 0.01,
        y=(bar_y0 + bar_y1) / 2,
        text="Higher RMSE<br>(worse)",
        showarrow=False,
        xanchor="left",
        font=dict(size=10, color="#94A3B8", family=FONT_FAMILY),
    )

    # ── 12. Layout ───────────────────────────────────────────────────────────
    height = max(380, 60 * n_models + 160)
    fig.update_layout(
        title=dict(
            text="Test RMSE Heatmap — All Models × All Targets",
            font=dict(family=FONT_FAMILY, size=16, color="#E2E8F0"),
        ),
        height=height,
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=PAPER_COLOR,
        font=dict(family=FONT_FAMILY, color="#CBD5E1"),
        margin=dict(l=160, r=30, t=60, b=100),
        xaxis=dict(
            side="top",
            tickfont=dict(color="#CBD5E1", size=12),
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#CBD5E1", size=12),
            showgrid=False,
            zeroline=False,
            autorange="reversed",
        ),
        hovermode="closest",
    )
    return fig


def build_rmse_heatmap_html(
    models_data: list[dict],
    scale_mode: str = "per_metric",
    sort_target: str | None = None,
    sort_dir: str | None = None,
) -> str:
    """
    Build a styled HTML table heatmap for RMSE comparison.

    Features:
    - Per-column or global color normalization
    - Row sorting by any target
    - Best-in-column gradient border highlight
    - Contrast-aware text (dark on light bg, light on dark bg)
    - Rank-aware hover tooltips
    - Custom gradient legend
    """
    targets   = list(TARGET_LABELS.keys())
    n_targets = len(targets)

    # ── 1. Raw data & labels ─────────────────────────────────────────────────
    raw_z = [
        [m["test_metrics"][t]["rmse"] for t in targets]
        for m in models_data
    ]
    m_labels = [
        f"👑 {m['label']}" if m.get("is_champion") else m["label"]
        for m in models_data
    ]
    n_models = len(models_data)

    # ── 2. Sort ──────────────────────────────────────────────────────────────
    order = list(range(n_models))
    if sort_target is not None and sort_dir is not None:
        col_idx = targets.index(sort_target)
        order.sort(key=lambda r: raw_z[r][col_idx],
                   reverse=(sort_dir == "desc"))
    raw_z    = [raw_z[r] for r in order]
    m_labels = [m_labels[r] for r in order]

    # ── 3. Rank per column (1 = best / lowest) ──────────────────────────────
    ranks = [[0] * n_targets for _ in range(n_models)]
    for c in range(n_targets):
        col_pairs = [(raw_z[r][c], r) for r in range(n_models)]
        col_pairs.sort(key=lambda x: x[0])
        for pos, (_, row) in enumerate(col_pairs, 1):
            ranks[row][c] = pos

    # ── 4. Best (min) per column ─────────────────────────────────────────────
    best_rows = []
    for c in range(n_targets):
        col_vals = [raw_z[r][c] for r in range(n_models)]
        best_rows.append(col_vals.index(min(col_vals)))

    # ── 5. Normalize ─────────────────────────────────────────────────────────
    if scale_mode == "per_metric":
        norm_z = [[0.0] * n_targets for _ in range(n_models)]
        for c in range(n_targets):
            col_vals = [raw_z[r][c] for r in range(n_models)]
            c_min, c_max = min(col_vals), max(col_vals)
            c_range = c_max - c_min if c_max != c_min else 1.0
            for r in range(n_models):
                norm_z[r][c] = (raw_z[r][c] - c_min) / c_range
        scale_label = "Scaled per metric (own min–max)"
    else:
        flat = [raw_z[r][c] for r in range(n_models) for c in range(n_targets)]
        g_min, g_max = min(flat), max(flat)
        g_range = g_max - g_min if g_max != g_min else 1.0
        norm_z = [
            [(raw_z[r][c] - g_min) / g_range for c in range(n_targets)]
            for r in range(n_models)
        ]
        scale_label = f"Scaled globally ({g_min:.2f}–{g_max:.2f})"

    # ── 6. Color helpers ─────────────────────────────────────────────────────
    def _cell_bg(t: float) -> str:
        r = int(219 + (30 - 219) * t)
        g = int(234 + (58 - 234) * t)
        b = int(254 + (95 - 254) * t)
        return f"rgb({r},{g},{b})"

    def _txt_color(t: float) -> str:
        return "#1E293B" if t < 0.55 else "#F1F5F9"

    # ── 7. Build header ──────────────────────────────────────────────────────
    col_labels = [TARGET_LABELS[t] for t in targets]
    TH = (
        "padding:0.7rem 0.9rem; color:#94A3B8; font-size:0.76rem; font-weight:700; "
        "text-transform:uppercase; letter-spacing:0.05em; text-align:center; "
        "border-bottom:2px solid rgba(0,200,255,0.18); white-space:nowrap;"
    )
    header = f'<th style="{TH} text-align:left; min-width:160px;">Model</th>'
    for lbl in col_labels:
        header += f'<th style="{TH}">{lbl}</th>'

    # ── 8. Build body rows ───────────────────────────────────────────────────
    rows = []
    for r in range(n_models):
        model_td = (
            f'<td style="padding:0.65rem 0.9rem; color:#CBD5E1; font-weight:600; '
            f'font-size:0.88rem; white-space:nowrap; '
            f'border-bottom:1px solid rgba(255,255,255,0.04);">{m_labels[r]}</td>'
        )
        cells = [model_td]
        for c in range(n_targets):
            bg = _cell_bg(norm_z[r][c])
            tc = _txt_color(norm_z[r][c])
            val = f"{raw_z[r][c]:.2f}"
            is_best = r == best_rows[c]

            if is_best:
                val += " ☆"
                bdr = (
                    "border:2.5px solid transparent; "
                    "border-image:linear-gradient(135deg, #00C8FF, #9D4EDD, #FF4D8D) 1;"
                )
            else:
                bdr = "border:1px solid rgba(255,255,255,0.04);"

            title = f"RMSE: {raw_z[r][c]:.4f} | Rank {ranks[r][c]} of {n_models}"

            cells.append(
                f'<td style="background:{bg}; color:{tc}; {bdr} '
                f'padding:0.65rem 0.8rem; text-align:center; font-size:0.95rem; '
                f"font-weight:700; font-family:'Space Grotesk',sans-serif;\" "
                f'title="{title}">{val}</td>'
            )
        rows.append(f'<tr>{"".join(cells)}</tr>')

    # ── 9. Gradient legend ───────────────────────────────────────────────────
    legend = (
        '<div style="display:flex; align-items:center; justify-content:center; '
        'gap:0.8rem; margin-top:0.8rem;">'
        '<span style="color:#94A3B8; font-size:0.78rem; font-weight:500;">'
        'Lower RMSE (better)</span>'
        '<div style="width:180px; height:10px; border-radius:5px; '
        'background:linear-gradient(90deg, #DBEAFE, #93C5FD, #3B82F6, #1D4ED8, #1E3A5F);"></div>'
        '<span style="color:#94A3B8; font-size:0.78rem; font-weight:500;">'
        'Higher RMSE (worse)</span>'
        '</div>'
    )

    # ── 10. Scale annotation ─────────────────────────────────────────────────
    scale_ann = (
        f'<div style="text-align:right; margin-bottom:0.4rem;">'
        f'<span style="color:#64748B; font-size:0.74rem; font-style:italic;">'
        f'{scale_label}</span></div>'
    )

    # ── 11. Footer ───────────────────────────────────────────────────────────
    footer = (
        '<div style="text-align:center; margin-top:0.35rem;">'
        '<span style="color:#64748B; font-size:0.72rem; font-style:italic;">'
        '☆ marks the best (lowest RMSE) model for that metric. '
        'Hover cells for rank details.</span></div>'
    )

    # ── 12. Assemble ─────────────────────────────────────────────────────────
    return f"""{scale_ann}<div style="overflow-x:auto; border-radius:16px;
    background:linear-gradient(180deg, rgba(15,23,42,0.82), rgba(8,13,31,0.70));
    border:1px solid rgba(0,200,255,0.12);
    box-shadow:0 18px 42px rgba(0,0,0,0.26); padding:2px;">
<table style="width:100%; border-collapse:separate; border-spacing:3px;">
<thead><tr>{header}</tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>
{legend}
{footer}"""
