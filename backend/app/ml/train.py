"""Phase 8: personalized PEF deterioration risk models + SHAP.
Target: PEF <80% of personal best (pef_best) for 2 consecutive days within 7 days.
RESEARCH/DEVELOPMENT ONLY — NOT CLINICALLY VALIDATED.
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from . import labels, dataset, clinical_gate

ART = Path(__file__).resolve().parents[3] / "artifacts" / "aamos00"
MODELS = Path(__file__).resolve().parents[3] / "models"
warnings.filterwarnings("ignore")

TARGET_CFG = dict(threshold_pct=80, consecutive_days=2, prediction_horizon_days=7)
CAT_COLS = ["age_range", "sex", "bmi_range", "severity", "smoker"]
TARGET = "candidate_target"


def load_xy():
    df = pd.read_parquet(ART / "feature_matrix.parquet")
    df[TARGET] = labels.candidate_target(df, "pef_best", **TARGET_CFG)
    df = df.dropna(subset=[TARGET])
    y = df[TARGET].astype(int)
    drop_cols = {"user_key", "date", TARGET, "baseline_expanding_max", "baseline_rolling_median"}
    feature_cols = [c for c in df.columns if c not in drop_cols and not c.startswith("trigger_")]
    X_num = df[feature_cols].copy()
    for c in ["daily_day_symp", "daily_night_symp", "daily_limit_activity"]:
        if c in X_num:
            X_num[c] = X_num[c].astype(str).str.lower().map({"true": 1.0, "false": 0.0})
    for c in CAT_COLS:
        if c in X_num:
            X_num[c] = X_num[c].astype("category").cat.codes.replace(-1, np.nan)
    # one-hot triggers
    trig = [c for c in df.columns if c.startswith("trigger_")]
    X = pd.concat([X_num, df[trig]], axis=1)
    return df, X, y


def metrics(y_true, proba, threshold=0.5):
    from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, confusion_matrix, brier_score_loss
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "roc_auc": round(roc_auc_score(y_true, proba), 4),
        "pr_auc": round(average_precision_score(y_true, proba), 4),
        "sensitivity": round(tp / (tp + fn), 4),
        "specificity": round(tn / (tn + fp), 4),
        "f1": round(f1_score(y_true, pred), 4),
        "brier": round(brier_score_loss(y_true, proba), 4),
    }


def main():
    clinical_gate.assert_training_allowed()
    df, X, y = load_xy()
    split = dataset.patient_level_split(df.user_key.unique(), seed=42)
    tr = df.user_key.isin(split["train"]); va = df.user_key.isin(split["val"]); te = df.user_key.isin(split["test"])
    Xtr, Xva, Xte = X[tr], X[va], X[te]; ytr, yva, yte = y[tr], y[va], y[te]

    # preprocessing fit on TRAIN only
    medians = Xtr.median(numeric_only=True)
    Xtr = Xtr.fillna(medians).fillna(0); Xva = Xva.fillna(medians).fillna(0); Xte = Xte.fillna(medians).fillna(0)

    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from xgboost import XGBClassifier
    from sklearn.isotonic import IsotonicRegression

    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=6, class_weight="balanced", random_state=42),
        "xgboost": XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.08, eval_metric="logloss", random_state=42),
    }
    results = {}
    fitted = {}
    for name, m in models.items():
        m.fit(Xtr, ytr)
        fitted[name] = m
        # calibrate on VALIDATION probabilities only (not train, not test)
        cal = IsotonicRegression(out_of_bounds="clip")
        cal.fit(m.predict_proba(Xva)[:, 1], yva)
        proba = cal.predict(m.predict_proba(Xte)[:, 1])
        raw = m.predict_proba(Xte)[:, 1]
        results[name] = {"metrics_calibrated": metrics(yte, proba), "metrics_raw": metrics(yte, raw)}

    split_summary = {
        "train_participants": len(split["train"]), "val_participants": len(split["val"]), "test_participants": len(split["test"]),
        "train_rows": int(tr.sum()), "val_rows": int(va.sum()), "test_rows": int(te.sum()),
        "train_positive_rate": round(float(ytr.mean()), 4), "test_positive_rate": round(float(yte.mean()), 4),
    }

    # participant-level eval (xgboost calibrated)
    from sklearn.isotonic import IsotonicRegression
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(fitted["xgboost"].predict_proba(Xva)[:, 1], yva)
    df_te = df[te].copy()
    df_te["proba"] = iso.predict(fitted["xgboost"].predict_proba(Xte)[:, 1])
    part = []
    for u, g in df_te.groupby("user_key"):
        yt = g[TARGET].astype(int); pr = (g.proba >= 0.5).astype(int)
        tp = int(((pr == 1) & (yt == 1)).sum()); fn = int(((pr == 0) & (yt == 1)).sum())
        tn = int(((pr == 0) & (yt == 0)).sum()); fp = int(((pr == 1) & (yt == 0)).sum())
        part.append({"participant_id": int(u), "prediction_days": len(g), "positive_events": int(yt.sum()),
                      "mean_predicted_risk": round(float(g.proba.mean()), 3), "max_predicted_risk": round(float(g.proba.max()), 3),
                      "actual_event_rate": round(float(yt.mean()), 3),
                      "sensitivity": round(tp / (tp + fn), 3) if tp + fn else None,
                      "specificity": round(tn / (tn + fp), 3) if tn + fp else None})

    # SHAP on xgboost raw model
    import shap
    expl = shap.TreeExplainer(fitted["xgboost"])
    sv = expl.shap_values(Xte)
    global_imp = pd.Series(np.abs(sv).mean(axis=0), index=Xte.columns).sort_values(ascending=False)

    MODELS.mkdir(exist_ok=True)
    import joblib
    joblib.dump(fitted["xgboost"], MODELS / "phase8_xgboost.pkl")

    # artifacts
    (ART / "model_comparison.csv").write_text(pd.DataFrame(results).T.to_csv())
    (ART / "split_summary.json").write_text(json.dumps(split_summary, indent=2))
    (ART / "model_metrics.json").write_text(json.dumps(results, indent=2))
    (ART / "calibration_metrics.json").write_text(json.dumps({k: v["metrics_calibrated"]["brier"] for k, v in results.items()}, indent=2))
    pd.DataFrame(part).to_csv(ART / "participant_level_metrics.csv", index=False)
    global_imp.rename("mean_abs_shap").to_csv(ART / "shap_global_importance.csv")
    (ART / "final_dataset_summary.json").write_text(json.dumps({
        "participants": int(df.user_key.nunique()), "rows": int(len(df)), "features": len(X.columns),
        "target": TARGET_CFG, "clinical_validation_status": "NOT_VALIDATED",
    }, indent=2))
    (ART / "final_target_summary.json").write_text(json.dumps({
        "target": "pef_deterioration", "definition": "PEF <80% personal best for 2 consecutive days within 7 days",
        "label": labels.LABEL, "events": int(y.sum()), "rate": round(float(y.mean()), 4),
    }, indent=2))
    print(json.dumps({"split": split_summary, "results": results, "top_shap": global_imp.head(5).to_dict()}, indent=2))
    return results


if __name__ == "__main__":
    main()
