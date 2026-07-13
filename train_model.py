"""
Trains the 30-day hospital readmission risk model used by app/ml/predictor.py.
Run once (or whenever the training data changes) to regenerate model.pkl / scaler.pkl.
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "hospital_readmissions_30k.csv")

df = pd.read_csv(DATA_PATH)

# ---- Feature engineering (mirrors app/ml/feature_engineering.py) ----
df["systolic_bp"] = df["blood_pressure"].str.split("/").str[0].astype(int)
df["diastolic_bp"] = df["blood_pressure"].str.split("/").str[1].astype(int)

gender_map = {"Male": 0, "Female": 1, "Other": 2}
dest_map = {"Home": 0, "Rehab": 1, "Nursing_Facility": 2}
yn_map = {"No": 0, "Yes": 1}

df["gender_enc"] = df["gender"].map(gender_map)
df["discharge_enc"] = df["discharge_destination"].map(dest_map)
df["diabetes_enc"] = df["diabetes"].map(yn_map)
df["hypertension_enc"] = df["hypertension"].map(yn_map)
df["target"] = df["readmitted_30_days"].map(yn_map)

feature_cols = [
    "age", "gender_enc", "systolic_bp", "diastolic_bp", "cholesterol", "bmi",
    "diabetes_enc", "hypertension_enc", "medication_count", "length_of_stay",
    "discharge_enc",
]

X = df[feature_cols]
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train_s, y_train)

probs = model.predict_proba(X_test_s)[:, 1]
preds = model.predict(X_test_s)
auc = roc_auc_score(y_test, probs)
print(f"AUC: {auc:.4f}")
print(classification_report(y_test, preds))

importances = dict(zip(feature_cols, model.feature_importances_))
for k, v in sorted(importances.items(), key=lambda x: -x[1]):
    print(f"{k:20s} {v:.4f}")

joblib.dump(model, os.path.join(BASE_DIR, "app", "ml", "model.pkl"))
joblib.dump(scaler, os.path.join(BASE_DIR, "app", "ml", "scaler.pkl"))
joblib.dump(feature_cols, os.path.join(BASE_DIR, "app", "ml", "feature_cols.pkl"))
print("Saved model.pkl, scaler.pkl, feature_cols.pkl")
