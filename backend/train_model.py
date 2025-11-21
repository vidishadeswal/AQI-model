# train_model_aqi.py
"""
Train an AQI model (time-aware).
Input: cleaned_aqi_dataset.csv (must contain datetimeLocal and AQI).
Output: aq_model_aqi_time.joblib (dict with model, features, lags)
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "cleaned_aqi_dataset.csv")
LAGS = 6

def add_time_features(time_series):
    hour = time_series.dt.hour
    dow = time_series.dt.weekday
    sin_hour = np.sin(2 * np.pi * hour / 24.0)
    cos_hour = np.cos(2 * np.pi * hour / 24.0)
    return pd.DataFrame({
        "sin_hour": sin_hour,
        "cos_hour": cos_hour,
        "dow": dow
    })

def prepare_df(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=["datetimeLocal"])
    df = df.rename(columns={"datetimeLocal":"datetime"})
    df = df.sort_values("datetime").reset_index(drop=True)
    # ensure AQI present
    if "AQI" not in df.columns:
        raise ValueError("AQI column not found in cleaned file.")
    df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
    df = df.dropna(subset=["AQI"]).reset_index(drop=True)

    # create lagged AQI
    for i in range(1, LAGS+1):
        df[f"aqi_lag_{i}"] = df["AQI"].shift(i)

    # target = next hour AQI, and target_time for time features
    df["target"] = df["AQI"].shift(-1)
    df["target_time"] = df["datetime"].shift(-1)

    df = df.dropna().reset_index(drop=True)

    # time features for target time
    tf = add_time_features(df["target_time"])
    df = pd.concat([df, tf], axis=1)

    # one-hot day-of-week (dow_0 ... dow_6)
    dow_dummies = pd.get_dummies(df["dow"], prefix="dow")
    df = pd.concat([df, dow_dummies], axis=1)

    return df

def main():
    df = prepare_df()
    # feature list order (important)
    features = [f"aqi_lag_{i}" for i in range(1, LAGS+1)] + ["sin_hour", "cos_hour"] + [c for c in df.columns if c.startswith("dow_")]
    X = df[features]
    y = df["target"]

    # time-series split (no shuffle)
    split = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = RandomForestRegressor(n_estimators=200, random_state=0, n_jobs=-1)
    print("Training RandomForestRegressor on AQI...")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Test MAE: {mae:.3f}")

    # Save model and metadata
    out = {"model": model, "features": features, "lags": LAGS}
    joblib.dump(out, "aq_model_aqi_time.joblib")
    print("Saved model to aq_model_aqi_time.joblib")

if __name__ == "__main__":
    main()
