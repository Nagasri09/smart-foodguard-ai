from pathlib import Path
import json
import numpy as np, pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data" / "demo" / "synthetic_demo.csv"
MODELS = BASE / "models"
FEATURES = ["temperature_c","ph","conductivity_us_cm","moisture_pct","color_index"]

def main():
    MODELS.mkdir(exist_ok=True)
    if not DATA.exists():
        raise SystemExit(f"Demo dataset missing: {DATA}")
    df = pd.read_csv(DATA)
    X, y = df[FEATURES], df["demo_label"]
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    model = Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler()),("classifier",RandomForestClassifier(n_estimators=120,random_state=42))])
    model.fit(X_train,y_train)
    pred = model.predict(X_test)
    joblib.dump(model, MODELS / "demo_model.joblib")
    meta = {"status":"Synthetic demonstration model trained","validated":False,"dataset_source":"Locally generated synthetic demonstration data",
      "dataset_rows":int(len(df)),"features":FEATURES,"target":"demo_label (synthetic)","algorithm":"RandomForestClassifier pipeline",
      "split":"75% train / 25% holdout; random_state=42; stratified","metrics":{"accuracy":accuracy_score(y_test,pred),
      "precision":precision_score(y_test,pred,zero_division=0),"recall":recall_score(y_test,pred,zero_division=0),
      "f1":f1_score(y_test,pred,zero_division=0),"confusion_matrix":confusion_matrix(y_test,pred).tolist()},
      "warning":"Metrics describe only synthetic generated labels. They are not scientific evidence or food-safety validation."}
    (MODELS / "model_metadata.json").write_text(json.dumps(meta,indent=2))
    print(json.dumps(meta,indent=2))
if __name__ == "__main__": main()
