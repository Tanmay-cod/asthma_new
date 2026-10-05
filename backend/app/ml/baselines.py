"""Personal baselines. All baselines at time T use strictly prior data."""
import numpy as np
import pandas as pd


def baseline_pef_best(patient_info: pd.DataFrame) -> pd.DataFrame:
    """Baseline A: static user-reported pef_best (available at registration)."""
    return patient_info[["user_key", "pef_best"]].rename(columns={"pef_best": "baseline_pef_best"})


def baseline_expanding_max(daily_pef: pd.DataFrame) -> pd.DataFrame:
    """Baseline B: baseline(T) = max(PEF strictly before T). Leakage-free via shift(1)."""
    df = daily_pef.sort_values(["user_key", "date"]).copy()
    df["baseline_expanding_max"] = df.groupby("user_key")["pef_max"].transform(lambda s: s.cummax().shift(1))
    return df[["user_key", "date", "baseline_expanding_max"]]


def baseline_rolling_median(daily_pef: pd.DataFrame, window: int = 14, min_periods: int = 3) -> pd.DataFrame:
    """Baseline C: trailing median over prior `window` days (no centering, no future)."""
    df = daily_pef.sort_values(["user_key", "date"]).copy()
    df["baseline_rolling_median"] = (
        df.groupby("user_key")["pef_max"]
          .transform(lambda s: s.shift(1).rolling(window, min_periods=min_periods).median())
    )
    return df[["user_key", "date", "baseline_rolling_median"]]
