"""Personalized asthma risk prediction with SHAP explainability."""
import json
import os
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")
EXPLAINER_PATH = os.path.join(MODEL_DIR, "shap_explainer.pkl")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "features.json")

FEATURES = [
    "spo2", "pulse", "temperature", "humidity", "dust",
    "pefr_pct_best",        # PEFR as % of user's personal best
    "delta_spo2",           # deviation from user's baseline SpO2
    "delta_pulse",          # deviation from user's baseline pulse
    "age",
    "smoking_score",        # never=0, former=1, current=2
]

SMOKING_MAP = {"never": 0, "former": 1, "current": 2}


def build_features(user, reading) -> dict:
    """Create personalized features: raw values + deviations from this user's baseline."""
    pefr_pct = (reading.pefr / user.personal_best_pefr * 100.0) if (reading.pefr and user.personal_best_pefr) else 90.0
    return {
        "spo2": reading.spo2,
        "pulse": reading.pulse,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "dust": reading.dust,
        "pefr_pct_best": pefr_pct,
        "delta_spo2": user.baseline_spo2 - reading.spo2,
        "delta_pulse": reading.pulse - user.baseline_pulse,
        "age": user.age,
        "smoking_score": SMOKING_MAP.get(str(user.smoking).lower(), 0),
    }


def predict_risk(user, reading) -> dict:
    features = build_features(user, reading)
    X = pd.DataFrame([features])[FEATURES]

    model = joblib.load(MODEL_PATH)
    proba = float(model.predict_proba(X)[0][1])  # probability of asthma exacerbation
    risk_score = round(proba * 100, 1)

    # SHAP explanation
    shap_values = {}
    try:
        import shap
        explainer = joblib.load(EXPLAINER_PATH)
        sv = explainer.shap_values(X)
        if isinstance(sv, list):  # older shap: list per class
            sv = sv[1]
        sv = np.array(sv).reshape(-1)
        shap_values = {f: round(float(v), 4) for f, v in zip(FEATURES, sv)}
    except Exception as e:
        shap_values = {f: round(features[f], 3) for f in FEATURES}  # fallback: raw values

    top = sorted(shap_values.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]
    top_factors = [{"feature": k, "contribution": v} for k, v in top]

    if risk_score < 30:
        level = "Low"
    elif risk_score < 65:
        level = "Moderate"
    else:
        level = "High"

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "shap_values": shap_values,
        "top_factors": top_factors,
        "features": {k: round(v, 2) for k, v in features.items()},
    }


def generate_synthetic_dataset(n=3000, seed=42) -> pd.DataFrame:
    """Synthetic training data mimicking asthma exacerbation conditions."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        pefr_pct = np.clip(rng.normal(88, 12), 50, 110)
        spo2 = np.clip(rng.normal(96, 1.6), 85, 100)
        pulse = np.clip(rng.normal(76, 12), 50, 140)
        dust = np.clip(rng.exponential(0.08), 0, 1.5)
        humidity = np.clip(rng.normal(55, 18), 15, 95)
        temperature = np.clip(rng.normal(27, 5), 10, 42)
        age = int(rng.integers(5, 80))
        smoking = rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1])

        # latent exacerbation logit (clinical intuition)
        logit = (
            0.55 * (100 - pefr_pct) / 10
            + 0.9 * max(0, 96 - spo2)
            + 0.04 * max(0, pulse - 85)
            + 1.6 * dust
            + 0.03 * max(0, humidity - 70)
            + 0.35 * smoking
            + 0.02 * max(0, age - 10) * (age > 60)
            - 1.2
        )
        p = 1 / (1 + np.exp(-logit))
        label = int(rng.random() < p)
        rows.append({
            "spo2": spo2, "pulse": pulse, "temperature": temperature,
            "humidity": humidity, "dust": dust, "pefr_pct_best": pefr_pct,
            "delta_spo2": max(0, 97 - spo2), "delta_pulse": max(0, pulse - 75),
            "age": age, "smoking_score": smoking, "label": label,
        })
    return pd.DataFrame(rows)


def train_model():
    from xgboost import XGBClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score
    import shap

    df = generate_synthetic_dataset()
    X = df[FEATURES]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.08,
                          eval_metric="logloss", random_state=42)
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    print(classification_report(y_test, (proba > 0.5).astype(int)))
    print("ROC-AUC:", round(roc_auc_score(y_test, proba), 4))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    explainer = shap.TreeExplainer(model)
    joblib.dump(explainer, EXPLAINER_PATH)
    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(FEATURES, f)
    print("Model + SHAP explainer saved to", MODEL_DIR)


if __name__ == "__main__":
    train_model()
