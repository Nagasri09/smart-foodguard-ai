from pathlib import Path
import json, joblib
import numpy as np
from app.ml.profiles import PROFILES

BASE = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE / "models" / "demo_model.joblib"
META_PATH = BASE / "models" / "model_metadata.json"

def model_info():
    if not META_PATH.exists():
        return {"status":"Model not trained", "validated":False, "message":"Run python -m app.ml.train"}
    return json.loads(META_PATH.read_text())

def predict(food, measurements):
    profile = PROFILES.get(food)
    if not profile:
        return {"result":"Insufficient data — unable to assess", "model_output":"No compatible food profile", "validated":False}
    required = profile["features"]
    if any(k not in measurements for k in required):
        return {"result":"Insufficient data — unable to assess", "model_output":"Required compatible measurements are missing", "validated":False}
    if not MODEL_PATH.exists():
        return {"result":"Insufficient data — unable to assess", "model_output":"Demo model unavailable; train it first", "validated":False}
    model = joblib.load(MODEL_PATH)
    all_features = ["temperature_c", "ph", "conductivity_us_cm", "moisture_pct", "color_index"]
    vector = np.array([[float(measurements[k]) if k in measurements else np.nan for k in all_features]])
    pred = int(model.predict(vector)[0])
    label = "Unusual pattern detected — further testing recommended" if pred == 1 else "No unusual pattern detected in the available measurements"
    return {"result":label, "model_output":"Synthetic demonstration model prediction", "validated":False,
            "notice":"SIMULATED DEMONSTRATION — NOT A REAL FOOD TEST"}
