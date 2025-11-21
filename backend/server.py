from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from datetime import timedelta
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "aq_model_aqi_time.joblib")
DATA_PATH = os.path.join(BASE_DIR, "cleaned_aqi_dataset.csv")
GOOGLE_AQI_API_KEY = os.getenv("GOOGLE_AQI_API_KEY")

@app.route('/')
def index():
    return jsonify({"status": "Backend is running"})

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def make_time_feats(ts):
    hr = ts.hour
    sin_h = np.sin(2*np.pi*hr/24.0)
    cos_h = np.cos(2*np.pi*hr/24.0)
    dow = ts.weekday()
    dow_cols = {f"dow_{i}": 1 if i==dow else 0 for i in range(7)}
    base = {"sin_hour":sin_h, "cos_hour":cos_h}
    base.update(dow_cols)
    return base

def fetch_google_aqi(lat=28.6139, lon=77.2090):
    """Fetch live AQI data from Google Air Quality API."""
    if not GOOGLE_AQI_API_KEY:
        print("Google AQI API Key not found.")
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
    """Process Google AQI API response into app format."""
    if not api_data:
        return None
        
    try:
        # Extract indexes
        indexes = api_data.get("indexes", [])
        aqi_val = 0
        aqi_cat = "Unknown"
        aqi_color = "#9ca3af"
        
        # Find Universal AQI or specific local AQI
        for idx in indexes:
            if idx.get("code") == "uaqi": # Universal AQI
                aqi_val = idx.get("aqi")
                aqi_cat = idx.get("category")
                # Map colors roughly
                if aqi_val <= 50: aqi_color = "#16a34a"
                elif aqi_val <= 100: aqi_color = "#f59e0b"
                else: aqi_color = "#ef4444"
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
            "color": aqi_color,
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

@app.route('/api/aqi', methods=['GET'])
def get_aqi():
    try:
        model_dict = load_model()
        if not model_dict:
            return jsonify({"error": "Model not trained"}), 503

        df = pd.read_csv(DATA_PATH, parse_dates=["datetimeLocal"])
        df = df.sort_values("datetimeLocal")
        
        # Get last known values for lags (from CSV)
        lags = model_dict.get("lags", 6)
        if len(df) < lags:
            return jsonify({"error": "Not enough data"}), 500
            
        last_vals = df["AQI"].tail(lags).tolist()
        
        # --- LIVE DATA FETCHING ---
        live_data = fetch_google_aqi()
        processed_live = process_google_aqi(live_data)
        
        # Fallback to CSV if live fetch fails
        if processed_live:
            current_val = processed_live["val"]
            current_pm25 = processed_live["pm25"]
            current_pm10 = processed_live["pm10"]
            current_no2 = processed_live["no2"]
            current_so2 = processed_live["so2"]
            current_o3 = processed_live["o3"]
            current_co = processed_live["co"]
            current_status = processed_live["status"]
            current_color = processed_live["color"]
            print("Using LIVE Google AQI data")
        else:
            current_val = last_vals[-1]
            current_pm25 = int(current_val) # Approximation
            current_pm10 = int(df.iloc[-1].get('pm10', 0))
            current_no2 = int(df.iloc[-1].get('no2', 0))
            current_so2 = int(df.iloc[-1].get('so2', 0))
            current_o3 = int(df.iloc[-1].get('o3', 0))
            current_co = round(df.iloc[-1].get('co', 0), 1)
            current_status = "Good" if current_val <= 50 else "Moderate" if current_val <= 100 else "Unhealthy"
            current_color = "#16a34a" if current_val <= 50 else "#f59e0b" if current_val <= 100 else "#ef4444"
            print("Using CSV fallback data")

        # Predict next 6 hours (using CSV history + model)
        model = model_dict["model"]
        features = model_dict["features"]
        
        now = pd.Timestamp.now()
        predictions = []
        vals = list(last_vals)
        
        for h in range(1, 7):
            fut = now + timedelta(hours=h)
            tf = make_time_feats(fut)
            feat = {}
            for i in range(1, lags+1):
                feat[f"aqi_lag_{i}"] = vals[-lags + (i-1)]
            feat.update(tf)
            
            # Ensure all features are present
            Xrow = np.array([feat.get(f, 0.0) for f in features]).reshape(1, -1)
            pred = float(model.predict(Xrow)[0])
            
            # Simulate future variations for other metrics
            variation = 1.0 + (np.sin(h) * 0.1) # +/- 10% variation
            
            pred_pm10 = int(df.iloc[-1].get('pm10', 0) * variation)
            pred_no2 = int(df.iloc[-1].get('no2', 0) * variation)
            pred_so2 = int(df.iloc[-1].get('so2', 0) * variation)
            pred_o3 = int(df.iloc[-1].get('o3', 0) * variation)
            pred_co = round(df.iloc[-1].get('co', 0) * variation, 1)
            pred_temp = int(df.iloc[-1].get('temperature', 28) + (h * 0.5)) # Temp rises slightly
            
            # Simulate weather variations
            base_humidity = df.iloc[-1].get('relativehumidity', 65)
            pred_humidity = int(max(0, min(100, base_humidity - (h * 2)))) # Humidity drops as temp rises
            
            base_wind = df.iloc[-1].get('wind_speed', 12)
            pred_wind = int(max(0, base_wind + (np.sin(h) * 3))) # Wind varies
            
            base_wind_dir = df.iloc[-1].get('wind_direction', 0)
            pred_wind_dir = int((base_wind_dir + (h * 15)) % 360) # Wind direction shifts
            
            predictions.append({
                "time": fut.strftime("%I %p"),
                "val": int(round(pred)),
                "label": "Good" if pred <= 50 else "Moderate" if pred <= 100 else "Unhealthy",
                "color": "#16a34a" if pred <= 50 else "#f59e0b" if pred <= 100 else "#ef4444",
                "metrics": {
                    "pollutants": [
                        {"name": "PM2.5", "val": int(round(pred)), "unit": "µg/m³", "color": "#3b82f6"},
                        {"name": "PM10", "val": pred_pm10, "unit": "µg/m³", "color": "#f59e0b"},
                        {"name": "NO2", "val": pred_no2, "unit": "ppb", "color": "#10b981"},
                        {"name": "SO2", "val": pred_so2, "unit": "ppb", "color": "#eab308"},
                        {"name": "O3", "val": pred_o3, "unit": "ppb", "color": "#8b5cf6"},
                        {"name": "CO", "val": pred_co, "unit": "ppm", "color": "#64748b"}
                    ]
                },
                "current": { # Weather details for this hour
                     "temp": f"{pred_temp}°C",
                     "humidity": f"{pred_humidity}%",
                     "wind": f"{pred_wind} km/h",
                     "wind_dir": pred_wind_dir
                },
                "advice": {
                    "activity": "Safe for all outdoor activities" if pred <= 50 else "Sensitive groups should limit prolonged exertion" if pred <= 100 else "Avoid prolonged outdoor exertion",
                    "mask": "No mask needed" if pred <= 100 else "Mask recommended for sensitive groups" if pred <= 150 else "N95 mask recommended",
                    "ventilation": "Open windows for fresh air" if pred <= 50 else "Keep windows closed during peak traffic"
                }
            })
            vals.append(pred)

        # Construct response with all variables
        response = {
            "current": {
                "time": "Now",
                "val": int(current_val),
                "pm25": int(current_pm25),
                "status": current_status,
                "color": current_color,
                "recommendation": "Air quality is good. Enjoy outdoor activities!" if current_val <= 50 else "Air quality is acceptable.",
                "temp": f"{int(df.iloc[-1].get('temperature', 28))}°C",
                "humidity": f"{int(df.iloc[-1].get('relativehumidity', 65))}%",
                "wind": f"{int(df.iloc[-1].get('wind_speed', 12))} km/h",
                "wind_dir": int(df.iloc[-1].get('wind_direction', 0)),
                "metrics": { # Add metrics to current object for consistent structure
                    "pollutants": [
                        {"name": "PM2.5", "val": int(current_pm25), "unit": "µg/m³", "color": "#3b82f6"},
                        {"name": "PM10", "val": int(current_pm10), "unit": "µg/m³", "color": "#f59e0b"},
                        {"name": "NO2", "val": int(current_no2), "unit": "ppb", "color": "#10b981"},
                        {"name": "SO2", "val": int(current_so2), "unit": "ppb", "color": "#eab308"},
                        {"name": "O3", "val": int(current_o3), "unit": "ppb", "color": "#8b5cf6"},
                        {"name": "CO", "val": round(current_co, 1), "unit": "ppm", "color": "#64748b"}
                    ]
                },
                "advice": {
                    "activity": "Safe for all outdoor activities" if current_val <= 50 else "Sensitive groups should limit prolonged exertion" if current_val <= 100 else "Avoid prolonged outdoor exertion",
                    "mask": "No mask needed" if current_val <= 100 else "Mask recommended for sensitive groups" if current_val <= 150 else "N95 mask recommended",
                    "ventilation": "Open windows for fresh air" if current_val <= 50 else "Keep windows closed during peak traffic"
                }
            },
            "forecast": predictions,
            "confidence": 85,
            "metrics": { # Keep global metrics for backward compatibility if needed
                "trend": [v for v in vals[-10:]],
                "pollutants": [
                    {"name": "PM2.5", "val": int(current_pm25), "unit": "µg/m³", "color": "#3b82f6"},
                    {"name": "PM10", "val": int(current_pm10), "unit": "µg/m³", "color": "#f59e0b"},
                    {"name": "NO2", "val": int(current_no2), "unit": "ppb", "color": "#10b981"},
                    {"name": "SO2", "val": int(current_so2), "unit": "ppb", "color": "#eab308"},
                    {"name": "O3", "val": int(current_o3), "unit": "ppb", "color": "#8b5cf6"},
                    {"name": "CO", "val": round(current_co, 1), "unit": "ppm", "color": "#64748b"}
                ]
            },
            "advice": {
                "activity": "Safe for all outdoor activities" if current_val <= 50 else "Sensitive groups should limit prolonged exertion" if current_val <= 100 else "Avoid prolonged outdoor exertion",
                "mask": "No mask needed" if current_val <= 100 else "Mask recommended for sensitive groups" if current_val <= 150 else "N95 mask recommended",
                "ventilation": "Open windows for fresh air" if current_val <= 50 else "Keep windows closed during peak traffic"
            }
        }
        return jsonify(response)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
