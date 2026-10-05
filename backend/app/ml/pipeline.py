"""End-to-end Phase 5 pipeline: build the ML-ready development dataset."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import ingestion, data_validation, aggregation, baselines, features, labels, leakage

ARTIFACTS = Path(__file__).resolve().parents[3] / "artifacts" / "aamos00"

# Candidate target configuration for DEVELOPMENT TESTING ONLY
CANDIDATE_TARGET = {
    "threshold_pct": 80,
    "consecutive_days": 2,
    "prediction_horizon_days": 7,
    "baseline_method": "expanding_max",
}


def main() -> dict:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    inventory = ingestion.build_inventory(ARTIFACTS / "data_inventory.json")

    tables = {name: ingestion.load_table(name) for name in
              ["patient_info", "daily", "weekly", "environment", "peakflow", "inhaler",
               "smartwatch1", "smartwatch2", "smartwatch3"]}
    report = data_validation.validate_all(tables)
    (ARTIFACTS / "data_validation_report.json").write_text(json.dumps(report, indent=2, default=str))

    daily_pef = aggregation.build_daily_pef(tables["peakflow"])
    exp_max = baselines.baseline_expanding_max(daily_pef)
    rolling = baselines.baseline_rolling_median(daily_pef)
    daily_pef = daily_pef.merge(exp_max, on=["user_key", "date"]).merge(rolling, on=["user_key", "date"])
    daily_pef = daily_pef.merge(baselines.baseline_pef_best(tables["patient_info"]), on="user_key")

    # HR daily
    hr = pd.concat([tables["smartwatch1"], tables["smartwatch2"], tables["smartwatch3"]], ignore_index=True)
    hr_daily = hr.groupby(["user_key", "date"], as_index=False)["hr"].median().rename(columns={"hr": "hr_median"})
    hr_feats = features.hr_features_at(hr_daily, daily_pef)

    env_feats = features.env_features(tables["environment"])
    sym_feats = features.symptom_features(tables["daily"])
    med_feats = features.medication_features(tables["daily"], tables["inhaler"])
    trig_feats, vocab = features.encode_triggers(tables["daily"])

    df = (daily_pef
          .merge(hr_feats, on=["user_key", "date"], how="left")
          .merge(env_feats, on=["user_key", "date"], how="left")
          .merge(sym_feats, on=["user_key", "date"], how="left")
          .merge(med_feats, on=["user_key", "date"], how="left")
          .merge(trig_feats, on=["user_key", "date"], how="left"))

    static = tables["patient_info"][["user_key", "age_range", "sex", "bmi_range", "severity", "smoker", "pack_years", "pef_best", "max_pef_expected"]]
    df = df.merge(static, on="user_key", how="left")

    # Candidate target (development config only)
    df["candidate_target"] = labels.candidate_target(df, "baseline_expanding_max",
                                                     CANDIDATE_TARGET["threshold_pct"],
                                                     CANDIDATE_TARGET["consecutive_days"],
                                                     CANDIDATE_TARGET["prediction_horizon_days"])

    # Leakage assertions
    leakage.assert_no_forbidden_features(df.columns)
    leakage.assert_no_future_features(df, daily_pef)
    leakage.assert_baseline_uses_only_prior(daily_pef, "baseline_expanding_max")

    # Drop cold-start rows (need baseline)
    before = len(df)
    df = df.dropna(subset=["baseline_expanding_max"])
    cold_start_removed = before - len(df)

    df.to_parquet(ARTIFACTS / "feature_matrix.parquet", index=False)

    metadata = {
        "clinical_validation_status": "NOT_VALIDATED",
        "candidate_target": CANDIDATE_TARGET,
        "candidate_target_label": labels.LABEL,
        "feature_names": [c for c in df.columns if c not in ("user_key", "date", "candidate_target")],
        "trigger_vocab": vocab,
        "cold_start_rows_removed": cold_start_removed,
    }
    (ARTIFACTS / "feature_metadata.json").write_text(json.dumps(metadata, indent=2))

    summary = {
        "participants": int(df.user_key.nunique()),
        "prediction_rows": int(len(df)),
        "n_features": len(metadata["feature_names"]),
        "date_coverage": [int(df.date.min()), int(df.date.max())],
        "pef_coverage_rows": int(df.pef_max.notna().sum()),
        "hr_coverage_rows": int(df.hr_median_7d.notna().sum()),
        "symptom_coverage": int(df.daily_day_symp.notna().sum()),
        "medication_coverage": int(df.daily_relief_inhaler.notna().sum()),
        "environment_coverage": int(df.temperature_mean_7d.notna().sum()),
        "cold_start_rows_removed": cold_start_removed,
        "candidate_target_distribution": df.candidate_target.value_counts().to_dict(),
        "clinical_validation_status": "NOT_VALIDATED",
    }
    (ARTIFACTS / "dataset_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
