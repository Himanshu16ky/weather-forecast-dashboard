# utils/data_loader.py
# ═══════════════════════════════════════════════════════════════════════════════
# Model discovery & metrics  → MLflow Model Registry (replaces ADLS metrics.json)
# Predictions                → ADLS (written by 04_daily_inference)
# Historical actuals         → Open-Meteo API
# ═══════════════════════════════════════════════════════════════════════════════

import os
import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import mlflow
from mlflow.tracking import MlflowClient

from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient

# ── ADLS paths (predictions only — metrics no longer needed here) ─────────────
PREDICTIONS_ROOT = "gold/predictions"

CITIES = [
    "Delhi", "Mumbai", "Chennai", "Kolkata",
    "Bengaluru", "Hyderabad", "Jaipur",
]

TARGET_COLS = [
    "temperature_2m",
    "windspeed_10m",
    "relativehumidity_2m",
    "cloudcover",
    "precipitation",
]

TARGET_LABELS = {
    "temperature_2m"       : "Temperature (°C)",
    "windspeed_10m"        : "Wind Speed (km/h)",
    "relativehumidity_2m"  : "Humidity (%)",
    "cloudcover"           : "Cloud Cover (%)",
    "precipitation"        : "Precipitation (mm)",
}

TARGET_ICONS = {
    "temperature_2m"       : "\U0001f321\ufe0f",
    "windspeed_10m"        : "\U0001f4a8",
    "relativehumidity_2m"  : "\U0001f4a7",
    "cloudcover"           : "\u2601\ufe0f",
    "precipitation"        : "\U0001f327\ufe0f",
}

TARGET_COLORS = {
    "temperature_2m"       : "#E63946",
    "windspeed_10m"        : "#457B9D",
    "relativehumidity_2m"  : "#2A9D8F",
    "cloudcover"           : "#778DA9",
    "precipitation"        : "#1D3557",
}


def champion_label(model: dict) -> str:
    """Return display label, prefixed with 👑 if this model is the current champion."""
    return f"👑 {model['label']} (Champion)" if model.get("is_champion") else model["label"]


# ═══════════════════════════════════════════════════════════════════════════════
# MLflow Client — replaces ADLS gold/model_metrics/metrics.json
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def get_mlflow_client() -> MlflowClient:
    """
    Create and cache MLflow client for Databricks workspace.

    Requires [databricks] section in .streamlit/secrets.toml:
        [databricks]
        host  = "https://adb-XXXX.azuredatabricks.net"
        token = "dapi..."
    """
    cfg = st.secrets["databricks"]
    os.environ["DATABRICKS_HOST"]  = cfg["host"]
    os.environ["DATABRICKS_TOKEN"] = cfg["token"]
    mlflow.set_tracking_uri("databricks")
    mlflow.set_registry_uri("databricks")
    return MlflowClient()


# ═══════════════════════════════════════════════════════════════════════════════
# ADLS Client — still needed for predictions
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def get_adls_client():
    """Create and cache ADLS client using Streamlit secrets."""
    cfg = st.secrets["azure"]
    credential = ClientSecretCredential(
        tenant_id     = cfg["tenant_id"],
        client_id     = cfg["client_id"],
        client_secret = cfg["client_secret"],
    )
    service_client = DataLakeServiceClient(
        account_url=f"https://{cfg['storage_account']}.dfs.core.windows.net",
        credential=credential,
    )
    return service_client.get_file_system_client(cfg["container"])


def _read_parquet(fs_client, path: str) -> pd.DataFrame:
    file_client = fs_client.get_file_client(path)
    data        = file_client.download_file().readall()
    return pd.read_parquet(io.BytesIO(data))


# ═══════════════════════════════════════════════════════════════════════════════
# Model Discovery & Metrics — direct from MLflow
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def get_available_models() -> list[dict]:
    """
    Discover Production models directly from MLflow Model Registry.

    Returns the structure:
        [{ label, model_key, config, val_metrics, test_metrics, horizon_metrics }]
    """
    client = get_mlflow_client()

    result = []
    for rm in client.search_registered_models():
        if not rm.name.startswith("weather-forecast-"):
            continue

        # ── Find the Production version ───────────────────────────────────
        versions = client.search_model_versions(f"name='{rm.name}'")
        prod_mv  = None
        for mv in versions:
            if mv.current_stage == "Production":
                prod_mv = mv
                break
        if not prod_mv:
            continue

        # ── Fetch run params + metrics from MLflow ────────────────────────
        if not prod_mv.run_id:
            print(f"Warning: Model '{rm.name}' version '{prod_mv.version}' has no run_id. Skipping.")
            continue
            
        run     = client.get_run(prod_mv.run_id)
        params  = run.data.params
        metrics = run.data.metrics

        model_name = rm.name
        model_key  = (
            model_name
            .replace("weather-forecast-", "")
            .replace("-", "_")
            + f"_v{prod_mv.version}"
        )
        label = (
            model_name
            .replace("weather-forecast-", "")
            .replace("-", " ")
            .upper()
        )

        # ── Config from MLflow params ─────────────────────────────────────
        # Key mapping: model_registery logs "model" as the architecture name
        config = {
            "architecture"  : params.get("model",         "unknown"),
            "hidden_size"   : params.get("hidden_size",   "unknown"),
            "num_layers"    : params.get("num_layers",    "unknown"),
            "dropout"       : params.get("dropout",       "unknown"),
            "input_len"     : params.get("input_len",     "unknown"),
            "output_len"    : params.get("output_len",    "unknown"),
            "n_features"    : params.get("n_features",    "unknown"),
            "n_targets"     : params.get("n_targets",     "unknown"),
            "targets"       : TARGET_COLS,
            "train_years"   : params.get("train_years",   "unknown"),
            "val_year"      : params.get("val_year",      "unknown"),
            "test_year"     : params.get("test_year",     "unknown"),
            "loss_fn"       : params.get("loss_fn",       "unknown"),
            "optimizer"     : params.get("optimizer",     "unknown"),
            "batch_size"    : params.get("batch_size",    "unknown"),
            "learning_rate" : params.get("learning_rate", "unknown"),
            "cities"        : params.get("cities",        "unknown"),
        }

        # ── Validation metrics ────────────────────────────────────────────
        val_metrics = {
            "best_val_loss": metrics.get("best_val_loss"),
        }

        # ── Test metrics per target (from flat MLflow metric keys) ────────
        # model_registery logs: test_mae_{target}, test_rmse_{target}
        test_metrics = {}
        for target in TARGET_COLS:
            target_data = {}
            mae_val  = metrics.get(f"test_mae_{target}")
            rmse_val = metrics.get(f"test_rmse_{target}")
            if mae_val is not None:
                target_data["mae"] = mae_val
            if rmse_val is not None:
                target_data["rmse"] = rmse_val
            if target_data:
                test_metrics[target] = target_data

        # ── Horizon metrics (from flat MLflow metric keys) ────────────────
        # model_registery logs: test_mae_{target}_{horizon_key}
        horizon_metrics = {}
        for target in TARGET_COLS:
            target_horizons = {}
            prefix = f"test_mae_{target}_"
            for key, val in metrics.items():
                if key.startswith(prefix) and key != f"test_mae_{target}":
                    h_key = key[len(prefix):]
                    target_horizons[h_key] = val
            if target_horizons:
                horizon_metrics[target] = target_horizons
        #line 219 to 230 is new
        # ── Champion tag ──────────────────────────────────────────────────
        # Set by the daily champion-selection job via:
        #   client.set_model_version_tag(rm.name, prod_mv.version, "champion", "true")
        # Falls back to checking the registered model tag as well.
        version_tags = prod_mv.tags or {}
        model_tags   = rm.tags   or {}
        is_champion  = (
            version_tags.get("champion", "").lower() == "true"
            or model_tags.get("champion", "").lower() == "true"
        )

        result.append({
            "label"          : label,
            "model_key"      : model_key,
            "config"         : config,
            "val_metrics"    : val_metrics,
            "test_metrics"   : test_metrics,
            "horizon_metrics": horizon_metrics,
            "is_champion"    : is_champion,
        })
        # in above is_champoin is new
        #in below initally only result was returned directly
    # Sort: champion first, then alphabetically
    result.sort(key=lambda m: (not m["is_champion"], m["label"]))
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Predictions — still from ADLS (written by 04_daily_inference)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800, show_spinner=False)
def get_available_dates(model_key: str, city: str) -> list[str]:
    """List all run_dates available for a model+city combination."""
    fs   = get_adls_client()
    path = f"{PREDICTIONS_ROOT}/model={model_key}/city={city}"
    try:
        paths = fs.get_paths(path)
        dates = sorted(set(
            p.name.split("run_date=")[-1].split("/")[0]
            for p in paths
            if "run_date=" in p.name
        ), reverse=True)
        return dates
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def load_predictions(model_key: str, city: str, run_date: str) -> pd.DataFrame:
    """Load predictions for a specific model, city and run_date."""
    fs   = get_adls_client()
    path = f"{PREDICTIONS_ROOT}/model={model_key}/city={city}/run_date={run_date}/predictions.parquet"
    try:
        df = _read_parquet(fs, path)
        df["forecast_timestamp"] = pd.to_datetime(df["forecast_timestamp"])
        return df
    except Exception as e:
        st.error(f"Could not load predictions: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# Historical Actuals — from Open-Meteo archive API (unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def load_historical_actuals(city: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch actual observed weather from Open-Meteo archive API.
    Note: archive API has a ~5 day lag — very recent dates won't be available.
    """
    import requests

    archive_cutoff = date.today() - timedelta(days=5)
    requested_end  = date.fromisoformat(end_date)
    if requested_end > archive_cutoff:
        st.info(
            f"\U0001f4c5 Actuals not yet available for {end_date} — "
            f"the Open-Meteo archive API has a ~5 day lag. "
            f"Check back after {(requested_end + timedelta(days=5)).strftime('%b %d')}."
        )
        return pd.DataFrame()

    CITY_COORDS = {
        "Delhi"     : (28.6139, 77.2090),
        "Mumbai"    : (19.0760, 72.8777),
        "Chennai"   : (13.0827, 80.2707),
        "Kolkata"   : (22.5726, 88.3639),
        "Bengaluru" : (12.9716, 77.5946),
        "Hyderabad" : (17.3850, 78.4867),
        "Jaipur"    : (26.9124, 75.7873),
    }

    lat, lon = CITY_COORDS[city]
    url      = "https://archive-api.open-meteo.com/v1/archive"
    params   = {
        "latitude"   : lat,
        "longitude"  : lon,
        "start_date" : start_date,
        "end_date"   : end_date,
        "hourly"     : "temperature_2m,windspeed_10m,relativehumidity_2m,cloudcover,precipitation",
        "timezone"   : "Asia/Kolkata",
    }

    try:
        r    = requests.get(url, params=params, timeout=15)
        resp = r.json()
        if "hourly" not in resp:
            reason = resp.get("reason", str(resp))
            st.error(f"Archive API error: {reason}")
            return pd.DataFrame()
        data = resp["hourly"]
        df   = pd.DataFrame({
            "timestamp"           : pd.to_datetime(data["time"]),
            "temperature_2m"      : data["temperature_2m"],
            "windspeed_10m"       : data["windspeed_10m"],
            "relativehumidity_2m" : data["relativehumidity_2m"],
            "cloudcover"          : data["cloudcover"],
            "precipitation"       : data["precipitation"],
        })
        return df
    except Exception as e:
        st.error(f"Could not fetch actuals: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    import json

    SEP = "=" * 60

    # ──────────────────────────────────────────────────────────────
    # 1. get_available_models()
    # ----------------------------------------------------------------
    print(f"\n{SEP}")
    print("TEST 1 - get_available_models()")
    print(SEP)
    available_models = get_available_models()
    if not available_models:
        print("  [WARN] No models returned (check MLflow/Databricks credentials).")
    for entry in available_models:
        print(json.dumps(entry, indent=4))
        print("-" * 40)

    # ──────────────────────────────────────────────────────────────
    # 2. get_adls_client()
    # ----------------------------------------------------------------
    print(f"\n{SEP}")
    print("TEST 2 - get_adls_client()")
    print(SEP)
    try:
        fs_client = get_adls_client()
        print(f"  [OK]  ADLS filesystem client created: {type(fs_client).__name__}")
    except Exception as exc:
        print(f"  [ERR] get_adls_client() raised: {exc}")
        fs_client = None

    # ──────────────────────────────────────────────────────────────
    # 3. get_available_dates(model_key, city)
    # ----------------------------------------------------------------
    print(f"\n{SEP}")
    print("TEST 3 - get_available_dates(model_key, city)")
    print(SEP)

    # Pick the first model and iterate over all cities
    if available_models:
        first_model_key = available_models[0]["model_key"]
        print(f"  Using model_key = '{first_model_key}'")
        for city in CITIES:
            dates = get_available_dates(first_model_key, city)
            if dates:
                print(f"  {city:12s} -> {len(dates)} date(s), latest: {dates[0]}")
            else:
                print(f"  {city:12s} -> [no dates found]")
    else:
        print("  [SKIP] No models available - cannot test get_available_dates().")

    # ----------------------------------------------------------------
    # 4. load_predictions(model_key, city, run_date)
    # ----------------------------------------------------------------
    print(f"\n{SEP}")
    print("TEST 4 - load_predictions(model_key, city, run_date)")
    print(SEP)

    if available_models:
        # Find the first (model, city, date) combo that has data
        found_combo = None
        for model in available_models:
            for city in CITIES:
                dates = get_available_dates(model["model_key"], city)
                if dates:
                    found_combo = (model["model_key"], city, dates[0])
                    break
            if found_combo:
                break

        if found_combo:
            mk, city, run_date = found_combo
            print(f"  model_key={mk!r}, city={city!r}, run_date={run_date!r}")
            preds_df = load_predictions(mk, city, run_date)
            if preds_df.empty:
                print("  [WARN] Returned empty DataFrame.")
            else:
                print(f"  [OK]  Shape: {preds_df.shape}")
                print(f"  Columns  : {list(preds_df.columns)}")
                print(f"  Date range: {preds_df['forecast_timestamp'].min()} -> {preds_df['forecast_timestamp'].max()}")
                print("  First 3 rows:")
                print(preds_df.head(3).to_string(index=False))
        else:
            print("  [SKIP] No (model, city, date) combo with data found.")
    else:
        print("  [SKIP] No models available - cannot test load_predictions().")

    # ----------------------------------------------------------------
    # 5. load_historical_actuals(city, start_date, end_date)
    # ----------------------------------------------------------------
    print(f"\n{SEP}")
    print("TEST 5 - load_historical_actuals(city, start_date, end_date)")
    print(SEP)

    from datetime import date, timedelta
    # Use a date range safely within the ~5-day archive lag
    end_dt   = date.today() - timedelta(days=7)   # 7 days ago - safely in archive
    start_dt = end_dt - timedelta(days=2)          # 3-day window
    start_str = start_dt.isoformat()
    end_str   = end_dt.isoformat()

    test_city = "Delhi"  # change to any city from CITIES list
    print(f"  city={test_city!r}, start={start_str!r}, end={end_str!r}")
    actuals_df = load_historical_actuals(test_city, start_str, end_str)
    if actuals_df.empty:
        print("  [WARN] Returned empty DataFrame (API lag or error).")
    else:
        print(f"  [OK]  Shape: {actuals_df.shape}")
        print(f"  Columns   : {list(actuals_df.columns)}")
        print(f"  Date range: {actuals_df['timestamp'].min()} -> {actuals_df['timestamp'].max()}")
        print("  First 5 rows:")
        print(actuals_df.head(5).to_string(index=False))

    print(f"\n{SEP}")
    print("ALL TESTS DONE - all 5 functions exercised.")
    print(SEP)