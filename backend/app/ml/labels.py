"""Candidate target generator. NOT clinically validated."""
import itertools

import numpy as np
import pandas as pd

CLINICAL_VALIDATION_STATUS = "NOT_VALIDATED"
LABEL = "CANDIDATE TARGET — NOT CLINICALLY VALIDATED"


def candidate_target(daily_pef: pd.DataFrame, baseline_col: str,
                     threshold_pct: float, consecutive_days: int,
                     prediction_horizon_days: int) -> pd.Series:
    """For each (user, date T): 1 if PEF < threshold_pct% of baseline for >=
    consecutive_days consecutive days within (T, T+H]; else 0.
    Features at T use <= T; target uses only future days."""
    df = daily_pef.sort_values(["user_key", "date"]).copy()
    targets = pd.Series(index=df.index, dtype="float64")
    for u, g in df.groupby("user_key"):
        g = g.reset_index()
        pef = g["pef_max"].to_numpy(dtype=float)
        base = g[baseline_col].to_numpy(dtype=float)
        below = (pef < threshold_pct / 100.0 * base) & ~np.isnan(base)
        for i in range(len(g)):
            window = below[i + 1: i + 1 + prediction_horizon_days]
            run, event = 0, False
            for v in window:
                run = run + 1 if v else 0
                if run >= consecutive_days:
                    event = True
            targets.loc[g.loc[i, "index"]] = float(event)
    return targets


BASELINE_METHODS = {"expanding_max", "pef_best", "rolling_median"}


def validate_config(cfg: dict) -> None:
    if not (0 < cfg["threshold_pct"] <= 100):
        raise ValueError("threshold_pct must be in (0, 100]")
    if cfg["consecutive_days"] < 1:
        raise ValueError("consecutive_days must be >= 1")
    if cfg["prediction_horizon_days"] < 1:
        raise ValueError("prediction_horizon_days must be >= 1")
    if cfg.get("baseline_method", "expanding_max") not in BASELINE_METHODS:
        raise ValueError(f"unsupported baseline_method; use one of {BASELINE_METHODS}")


def candidate_configs() -> list[dict]:
    return [
        {"threshold_pct": t, "consecutive_days": n, "prediction_horizon_days": h, "baseline_method": "expanding_max"}
        for t, n, h in itertools.product([60, 70, 75, 80, 85, 90], [1, 2, 3], [1, 3, 7, 14])
    ]
