"""Phase 6: descriptive sensitivity analysis of candidate PEF targets.
No model training. Development-only analysis."""
import json
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
import pandas as pd

from . import ingestion, aggregation, baselines, labels

ARTIFACTS = Path(__file__).resolve().parents[3] / "artifacts" / "aamos00"

THRESHOLDS = [60, 70, 75, 80, 85, 90]
PERSISTENCE = [1, 2, 3]
HORIZONS = [1, 3, 7, 14]


def _baseline_series(daily_pef: pd.DataFrame, patient_info: pd.DataFrame, method: str) -> pd.Series:
    if method == "expanding_max":
        return baselines.baseline_expanding_max(daily_pef).set_index(["user_key", "date"])["baseline_expanding_max"]
    if method == "rolling_median":
        return baselines.baseline_rolling_median(daily_pef).set_index(["user_key", "date"])["baseline_rolling_median"]
    if method == "pef_best":
        pb = baselines.baseline_pef_best(patient_info)
        m = daily_pef[["user_key", "date"]].merge(pb, on="user_key", how="left")
        return m.set_index(["user_key", "date"])["baseline_pef_best"]
    raise ValueError(method)


def _events_per_config(daily_pef, patient_info, thr, n, h, method):
    base = _baseline_series(daily_pef, patient_info, method)
    df = daily_pef.set_index(["user_key", "date"]).copy()
    df["baseline"] = base
    per_user = Counter()
    opp = 0; pos = 0; neg = 0
    days_between = defaultdict(list)
    last_event_day = {}
    for u, g in df.groupby(level=0):
        g = g.sort_values("date")
        pef = g["pef_max"].to_numpy(float)
        b = g["baseline"].to_numpy(float)
        below = (pef < thr / 100 * b) & ~np.isnan(b)
        for i in range(len(g)):
            if i + h >= len(g):
                continue
            opp += 1
            window = below[i + 1:i + 1 + h]
            run = 0; event = False
            for v in window:
                run = run + 1 if v else 0
                if run >= n:
                    event = True
            if event:
                pos += 1
                per_user[u] += 1
                d = g.index.get_level_values(1)[i]
                if u in last_event_day:
                    days_between[u].append(d - last_event_day[u])
                last_event_day[u] = d
            else:
                neg += 1
    return opp, pos, neg, per_user, days_between


def run_sensitivity() -> pd.DataFrame:
    tables = {k: ingestion.load_table(k) for k in ["patient_info", "peakflow"]}
    daily_pef = aggregation.build_daily_pef(tables["peakflow"])
    rows = []
    for thr in THRESHOLDS:
        for n in PERSISTENCE:
            for h in HORIZONS:
                opp, pos, neg, per_user, dbt = _events_per_config(daily_pef, tables["patient_info"], thr, n, h, "expanding_max")
                counts = list(per_user.values())
                gaps = [g for v in dbt.values() for g in v]
                rows.append({
                    "threshold_pct": thr, "consecutive_days": n, "prediction_horizon_days": h,
                    "baseline_method": "expanding_max",
                    "prediction_opportunities": opp, "positive_events": pos, "negative_events": neg,
                    "event_rate": round(pos / opp, 4) if opp else None,
                    "participants_with_events": len(per_user),
                    "participants_without_events": int(daily_pef.user_key.nunique() - len(per_user)),
                    "participant_event_rate": round(len(per_user) / max(daily_pef.user_key.nunique(), 1), 4),
                    "mean_events_per_participant": round(np.mean(counts), 2) if counts else 0,
                    "median_events_per_participant": round(float(np.median(counts)), 1) if counts else 0,
                    "max_events_per_participant": max(counts) if counts else 0,
                    "median_days_between_events": round(float(np.median(gaps)), 1) if gaps else None,
                })
    out = pd.DataFrame(rows)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    out.to_csv(ARTIFACTS / "target_sensitivity.csv", index=False)
    return out


def run_baseline_sensitivity() -> pd.DataFrame:
    tables = {k: ingestion.load_table(k) for k in ["patient_info", "peakflow"]}
    daily_pef = aggregation.build_daily_pef(tables["peakflow"])
    rows = []
    for thr, n, h in [(80, 2, 7), (85, 2, 7)]:
        for method in ["pef_best", "expanding_max", "rolling_median"]:
            opp, pos, neg, per_user, _ = _events_per_config(daily_pef, tables["patient_info"], thr, n, h, method)
            rows.append({"threshold_pct": thr, "consecutive_days": n, "prediction_horizon_days": h,
                         "baseline_method": method, "prediction_opportunities": opp,
                         "positive_events": pos, "event_rate": round(pos / opp, 4) if opp else None,
                         "participants_with_events": len(per_user),
                         "max_events_per_participant": max(per_user.values()) if per_user else 0})
    out = pd.DataFrame(rows)
    out.to_csv(ARTIFACTS / "baseline_sensitivity.csv", index=False)
    return out


if __name__ == "__main__":
    s = run_sensitivity()
    b = run_baseline_sensitivity()
    print(s.describe().to_string())
    print(b.to_string())
