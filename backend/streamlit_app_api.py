# streamlit_app_aqi_clean.py
"""
Prediction-only version with Outdoor Activity Planning & Warnings
- Keeps same filename
- Loads cleaned_aqi_dataset.csv (or fallback /mnt/data/cleaned_aqi_dataset.csv)
- Loads time-aware AQI model (aq_model_aqi_time.joblib preferred)
- Uses current IST time as prediction base
- Shows next 3-hour AQI predictions only
- Adds per-hour activity advice, mask recommendations and overall warnings
- INTEGRATES GOOGLE AQI API FOR LIVE DATA
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------- Config ----------
BASE_DIR = Path(__file__).resolve().parent
LOCAL_CLEANED = BASE_DIR / "cleaned_aqi_dataset.csv"
FALLBACK_CLEANED = Path("/mnt/data/cleaned_aqi_dataset.csv")   # session fallback (use this path if you need direct download)
MODEL_ORDER = [
    BASE_DIR / "aq_model_aqi_time.joblib",
    BASE_DIR / "aq_model_time.joblib",
    BASE_DIR / "aq_model.joblib",
    BASE_DIR / "aq_model_rf.joblib"
]
PRED_STEPS = 3
GOOGLE_AQI_API_KEY = os.getenv("GOOGLE_AQI_API_KEY")
# ----------------------------

st.set_page_config(page_title="AQI Nowcast — Predictions only", layout="wide")
st.title("AQI Nowcast — Live & Next 3 hours")
st.markdown("This view shows **Live AQI** (from Google API) and **Model Predictions** (based on historical data).")
st.markdown(f"**Data source:** `{FALLBACK_CLEANED}`  — [Download cleaned AQI dataset]({FALLBACK_CLEANED})")
st.markdown("---")

# ---------- Helpers ----------
def load_cleaned():
    if LOCAL_CLEANED.exists():
        p = LOCAL_CLEANED
    elif FALLBACK_CLEANED.exists():
        p = FALLBACK_CLEANED
    else:
        st.error("Cleaned AQI dataset not found. Place `cleaned_aqi_dataset.csv` in project folder or at `/mnt/data/cleaned_aqi_dataset.csv`.")
        st.stop()
    df = pd.read_csv(p, parse_dates=["datetimeLocal"])
    df = df.rename(columns={"datetimeLocal":"datetime"}).sort_values("datetime").reset_index(drop=True)
    # ensure numeric
    for c in ["AQI","pm25","pm10","no2","so2","o3","co","nh3"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    st.caption(f"Data loaded from: `{p}`")
    return df

def load_model():
    for name in MODEL_ORDER:
        if Path(name).exists():
            model_dict = joblib.load(name)
            st.caption(f"Loaded model: `{name}`")
            return model_dict
    st.warning("No model file found. Place `aq_model_aqi_time.joblib` in the folder or train the model.")
    st.stop()

def aqi_category_color(aqi):
    aqi = float(aqi)
    if aqi <= 50: return "Good", "#16a34a"
    if aqi <= 100: return "Moderate", "#f59e0b"
    if aqi <= 200: return "Unhealthy for sensitive groups", "#f97316"
    if aqi <= 300: return "Unhealthy", "#ef4444"
    if aqi <= 400: return "Very Unhealthy", "#9f1239"
    return "Hazardous", "#7c2d12"

def make_time_feats(ts):
    hr = ts.hour
    sin_h = np.sin(2*np.pi*hr/24.0)
    cos_h = np.cos(2*np.pi*hr/24.0)
    dow = ts.weekday()
    dow_cols = {f"dow_{i}": 1 if i==dow else 0 for i in range(7)}
    base = {"sin_hour":sin_h, "cos_hour":cos_h}
    base.update(dow_cols)
    return base

def predict_timeaware(model_dict, last_vals, base_time, steps=3):
    model = model_dict["model"]
    features = model_dict["features"]
    lags = model_dict.get("lags", len([f for f in features if f.startswith("aqi_lag_")]))
    vals = list(last_vals)
    results = []
    for h in range(1, steps+1):
        fut = pd.to_datetime(base_time) + timedelta(hours=h)
        tf = make_time_feats(fut)
        feat = {}
        for i in range(1, lags+1):
            feat[f"aqi_lag_{i}"] = vals[-lags + (i-1)]
        feat.update(tf)
        Xrow = np.array([feat.get(f, 0.0) for f in features]).reshape(1, -1)
        p = float(model.predict(Xrow)[0])
        results.append((fut, p))
        vals.append(p)
    return results

def predict_simple(model_dict, last_vals, base_time, steps=3):
    model = model_dict["model"]
    lags = model_dict.get("lags", len(last_vals))
    vals = list(last_vals)
    results=[]
    for h in range(1, steps+1):
        arr = np.array(vals[-lags:]).reshape(1, -1)
        p = float(model.predict(arr)[0])
        results.append((pd.to_datetime(base_time) + timedelta(hours=h), p))
        vals.append(p)
    return results

def hour_label(ts):
    return pd.to_datetime(ts).strftime("%I %p").lstrip("0").replace(" ","").lower()

# Map AQI category to concrete activity + mask advice
def activity_and_mask_for_category(cat):
    """Return (action_text, mask_text, emoji)"""
    if cat == "Good":
        return ("Safe for all outdoor activities", "No mask needed", "✅")
    if cat == "Moderate":
        return ("OK for most, sensitive individuals should limit long exertion", "Optional cloth/surgical mask", "🟡")
    if cat == "Unhealthy for sensitive groups":
        return ("Sensitive groups: reduce prolonged/outdoor heavy exercise", "Surgical mask recommended for sensitive persons", "🟠")
    if cat == "Unhealthy":
        return ("Limit outdoor activities; avoid prolonged or heavy exertion", "Surgical/N95 for vulnerable; consider N95 if outdoors", "🔴")
    if cat == "Very Unhealthy":
        return ("Avoid outdoor exertion; stay indoors if possible", "N95/FFP2 recommended if stepping out", "⚠️")
    return ("Stay indoors, avoid all outdoor activity", "N95/FFP2 required if you must go out", "☠️")

# --- Google AQI API Helpers ---
def fetch_google_aqi(lat=28.6139, lon=77.2090):
    """Fetch live AQI data from Google Air Quality API."""
    if not GOOGLE_AQI_API_KEY:
        return None

    url = f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={GOOGLE_AQI_API_KEY}"
    data = {
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "extraComputations": [
            "POLLUTANT_ADDITIONAL_INFO",
            "DOMINANT_POLLUTANT_CONCENTRATION",
            "POLLUTANT_CONCENTRATION",
            "LOCAL_AQI"
        ]
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Google AQI data: {e}")
        return None

def process_google_aqi(api_data):
    """Process Google AQI API response."""
    if not api_data:
        return None
        
    try:
        # Extract indexes
        indexes = api_data.get("indexes", [])
        aqi_val = 0
        aqi_cat = "Unknown"
        
        # Find Universal AQI or specific local AQI
        for idx in indexes:
            if idx.get("code") == "uaqi": # Universal AQI
                aqi_val = idx.get("aqi")
                aqi_cat = idx.get("category")
                break
        
        # Extract pollutants
        pollutants = api_data.get("pollutants", [])
        pollutant_map = {}
        for p in pollutants:
            code = p.get("code", "").lower()
            conc = p.get("concentration", {}).get("value", 0)
            pollutant_map[code] = conc
            
        return {
            "val": aqi_val,
            "status": aqi_cat,
            "pm25": pollutant_map.get("pm25", 0),
            "pm10": pollutant_map.get("pm10", 0),
            "no2": pollutant_map.get("no2", 0),
            "so2": pollutant_map.get("so2", 0),
            "o3": pollutant_map.get("o3", 0),
            "co": pollutant_map.get("co", 0)
        }
    except Exception as e:
        print(f"Error processing API data: {e}")
        return None

# ---------- Load ----------
df = load_cleaned()
model_dict = load_model()

# determine lags expected
lags = model_dict.get("lags", len([f for f in model_dict["features"] if f.startswith("aqi_lag_")]))
st.write(f"Model expects {lags} lag features (using last {lags} AQI readings).")

# get last observed AQI values (oldest->newest) for numeric inputs
if "AQI" not in df.columns:
    st.error("AQI column missing in dataset. Please include computed AQI.")
    st.stop()

last_vals = df["AQI"].dropna().tail(lags).tolist()
if len(last_vals) < lags:
    st.error(f"Not enough AQI readings in file (need {lags}).")
    st.stop()

# prediction base = current time (IST)
csv_last_time = pd.to_datetime(df["datetime"].dropna().tail(1).iloc[0])
now = pd.Timestamp.now(tz="Asia/Kolkata")
st.caption(f"CSV newest: {csv_last_time}  ·  Using current time (IST) as base: {now}")

if (now - csv_last_time).total_seconds() > 3*3600:
    st.warning("Latest CSV reading is older than 3 hours. Predictions from now may be less accurate.")

# ---------- Live Data Fetch ----------
live_data = fetch_google_aqi()
processed_live = process_google_aqi(live_data)

if processed_live:
    current_val = processed_live["val"]
    current_cat = processed_live["status"]
    _, current_color = aqi_category_color(current_val)
    source_label = "Live (Google API)"
else:
    # Fallback to CSV
    current_val = last_vals[-1]
    current_cat, current_color = aqi_category_color(current_val)
    source_label = "Historical (CSV Fallback)"

# ---------- Predictions only ----------
if ("sin_hour" in model_dict["features"]) or any(f.startswith("dow_") for f in model_dict["features"]):
    preds = predict_timeaware(model_dict, last_vals, now, steps=PRED_STEPS)
else:
    preds = predict_simple(model_dict, last_vals, now, steps=PRED_STEPS)

future_times = [t for t,_ in preds]
preds_only = [p for _,p in preds]

# Top: Big AQI card + gauge
col1, col2 = st.columns([2,1])
with col1:
    # Show Current Live Status
    st.markdown(f"<div style='padding:12px;border-radius:8px;background:#f7f7f8;box-shadow: 0 6px 20px rgba(0,0,0,0.04)'>"
                f"<h2 style='margin:0'>Current: {int(round(current_val))} <small style='color:#6b7280'>AQI</small></h2>"
                f"<div style='margin-top:6px;color:#374151'>Status: <strong style='color:{current_color}'>{current_cat}</strong></div>"
                f"<div style='font-size:0.8em;color:#6b7280;margin-top:4px'>Source: {source_label}</div>"
                f"</div>", unsafe_allow_html=True)
    
    st.markdown("#### Forecast (Next 3 Hours)")
    
    worst_val = max(preds_only)
    worst_cat, worst_color = aqi_category_color(worst_val)
    
    # simple color bar gauge
    figg, axg = plt.subplots(figsize=(8,0.5))
    cuts = [(0,50,"#16a34a"),(51,100,"#f59e0b"),(101,200,"#f97316"),(201,300,"#ef4444"),(301,400,"#9f1239"),(401,500,"#7c2d12")]
    for lo,hi,col in cuts:
        axg.barh(0, hi-lo, left=lo, height=0.5, color=col, edgecolor='none')
    axg.plot([current_val],[0], marker='o', color='white', markeredgecolor='black', markersize=8, label='Current')
    axg.plot([worst_val],[0], marker='v', color='black', markersize=10, label='Worst Predicted')
    axg.set_xlim(0,500); axg.set_yticks([]); axg.set_xlabel("AQI scale")
    for spine in axg.spines.values(): spine.set_visible(False)
    st.pyplot(figg)

with col2:
    st.markdown("<div style='padding:10px;border-radius:8px;background:#fbfbfc;box-shadow: 0 6px 18px rgba(0,0,0,0.03)'>", unsafe_allow_html=True)
    st.subheader("Predictions")
    for i,(p,t) in enumerate(zip(preds_only, future_times), start=1):
        lbl = hour_label(t)
        cat, color = aqi_category_color(p)
        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:6px 0;'>"
                    f"<div><strong>+{i} ({lbl})</strong><div style='color:#6b7280'>{cat}</div></div>"
                    f"<div style='text-align:right'><span style='font-size:20px;color:{color}'>{int(round(p))}</span></div>"
                    f"</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------- Predictions plot (ONLY predicted points) ----------
st.subheader("Predicted AQI (next 3 hours)")

fig, ax = plt.subplots(figsize=(10,3))
pred_times_pd = [pd.to_datetime(t) for t in future_times]
ax.plot(pred_times_pd, preds_only, marker='o', linestyle='--', color='#f97316', linewidth=2)
for x,y in zip(pred_times_pd, preds_only):
    ax.annotate(f"{int(round(y))}", (x,y), textcoords="offset points", xytext=(0,8), ha='center')

locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
formatter = mdates.DateFormatter("%I %p")
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

ax.set_ylim(0, max(500, max(preds_only) + 50))
ax.set_ylabel("AQI")
ax.set_xlabel("Time")
ax.set_title("Next 3-hour AQI predictions")
ax.grid(alpha=0.25)
fig.autofmt_xdate(rotation=15)
st.pyplot(fig)

# ---------- Bar chart for clarity ----------
fig2, ax2 = plt.subplots(figsize=(6,3))
labels = [hour_label(t) for t in future_times]
ax2.bar(labels, preds_only, color='#3b82f6', width=0.5)
ax2.set_ylabel("Predicted AQI")
ax2.set_title("Predicted AQI for next 3 hours")
ax2.grid(axis='y', alpha=0.2)
st.pyplot(fig2)

st.markdown("---")

# ---------- Outdoor activity planning & warnings ----------
st.subheader("Outdoor activity planning & warnings")

# per-hour advice table
planning_rows = []
for t, p in zip(future_times, preds_only):
    cat, _ = aqi_category_color(p)
    action, mask, emoji = activity_and_mask_for_category(cat)
    planning_rows.append({
        "time": pd.to_datetime(t).strftime("%Y-%m-%d %I:%M %p"),
        "AQI": int(round(p)),
        "category": cat,
        "advice": action,
        "mask": mask,
        "emoji": emoji
    })
plan_df = pd.DataFrame(planning_rows)

# show per-hour table
st.table(plan_df[["time","AQI","category","advice","mask","emoji"]].rename(columns={"emoji":""}))

# combined planning summary
# - worst predicted category determines strongest advice
cats = plan_df["category"].tolist()
order = ["Good","Moderate","Unhealthy for sensitive groups","Unhealthy","Very Unhealthy","Hazardous"]
worst = max(cats, key=lambda c: order.index(c))
# get mask/advice for worst
worst_action, worst_mask, worst_emoji = activity_and_mask_for_category(worst)

st.markdown(f"**Summary (next {PRED_STEPS} hours):** Worst predicted category: **{worst}** {worst_emoji}")
st.markdown(f"**Action:** {worst_action}")
st.markdown(f"**Mask recommendation:** {worst_mask}")

# additional explicit warnings depending on levels
warnings = []
if worst in ("Unhealthy","Very Unhealthy","Hazardous"):
    warnings.append("Avoid outdoor exercise. People with respiratory or cardiac conditions, children and older adults should stay indoors.")
if worst in ("Very Unhealthy","Hazardous"):
    warnings.append("If you must go outside, wear an N95/FFP2 mask and avoid crowded/traffic-heavy routes.")
if worst in ("Unhealthy for sensitive groups","Unhealthy","Very Unhealthy","Hazardous"):
    warnings.append("Consider moving outdoor activities to an indoor, well-ventilated area or rescheduling to a cleaner hour.")

if warnings:
    for w in warnings:
        st.warning(w)
else:
    st.success("No special warnings — normal outdoor activities are OK.")

st.markdown("---")

# ---------- Optional: pollutant mini charts ----------
st.subheader("Pollutant snapshots (recent)")
pcols = st.columns(3)
recent = df.tail(24)

with pcols[0]:
    st.markdown("**PM2.5 (recent)**")
    if "pm25" in recent.columns:
        figp, axp = plt.subplots(figsize=(3.5,1.8))
        axp.plot(recent["datetime"], recent["pm25"], marker='o', linewidth=1)
        axp.xaxis.set_major_formatter(mdates.DateFormatter("%I %p"))
        axp.set_ylabel("µg/m³")
        axp.grid(alpha=0.2)
        figp.autofmt_xdate(rotation=20)
        st.pyplot(figp)
    else:
        st.info("pm25 not in dataset")

with pcols[1]:
    st.markdown("**PM10 (recent)**")
    if "pm10" in recent.columns:
        figp2, axp2 = plt.subplots(figsize=(3.5,1.8))
        axp2.plot(recent["datetime"], recent["pm10"], marker='o', linewidth=1, color='#f59e0b')
        axp2.xaxis.set_major_formatter(mdates.DateFormatter("%I %p"))
        axp2.set_ylabel("µg/m³")
        axp2.grid(alpha=0.2)
        figp2.autofmt_xdate(rotation=20)
        st.pyplot(figp2)
    else:
        st.info("pm10 not in dataset")

with pcols[2]:
    st.markdown("**AQI contributors (latest)**")
    sub_cols = [c for c in df.columns if c.endswith("_sub")]
    if len(sub_cols) > 0:
        latest = df.tail(1)
        subs = {c.replace("_sub",""): float(latest[c].values[0]) if not pd.isna(latest[c].values[0]) else 0.0 for c in sub_cols}
        items = dict(sorted(subs.items(), key=lambda x: x[1], reverse=True)[:5])
        figp3, axp3 = plt.subplots(figsize=(3.5,1.8))
        axp3.bar(items.keys(), items.values(), color=['#16a34a','#f59e0b','#f97316','#ef4444','#9f1239'][:len(items)])
        axp3.grid(axis='y', alpha=0.2)
        st.pyplot(figp3)
    else:
        st.info("No pollutant sub-index columns available")

st.markdown("---")
st.write("Note: Advice is automatic guidance based on predicted AQI categories. If you or someone in your household has a serious respiratory condition, always follow clinician guidance.")
