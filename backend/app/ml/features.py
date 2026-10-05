"""Temporal feature engineering. Every feature uses data with date <= prediction time T."""
import numpy as np
import pandas as pd


def _trailing(df: pd.DataFrame, user_col: str, date_col: str, value_col: str,
              window: int, T: int, user: int) -> pd.Series:
    sub = df[(df[user_col] == user) & (df[date_col] <= T) & (df[date_col] > T - window)]
    return sub[value_col]


def hr_features_at(hr_daily: pd.DataFrame, daily_pef: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """hr_daily: user_key,date,hr_median (from smartwatch). Joins onto daily_pef dates."""
    out = []
    for (u, t), g in daily_pef.groupby(["user_key", "date"]):
        vals = hr_daily[(hr_daily.user_key == u) & (hr_daily.date <= t) & (hr_daily.date > t - window)]["hr_median"].dropna()
        base = hr_daily[(hr_daily.user_key == u) & (hr_daily.date < t)]["hr_median"].dropna()
        out.append({
            "user_key": u, "date": t,
            "hr_median_7d": vals.median() if len(vals) else np.nan,
            "hr_min_7d": vals.min() if len(vals) else np.nan,
            "hr_max_7d": vals.max() if len(vals) else np.nan,
            "hr_variability_7d": vals.std() if len(vals) > 1 else np.nan,
            "hr_baseline": base.median() if len(base) else np.nan,
        })
    df = pd.DataFrame(out)
    df["hr_deviation"] = df["hr_median_7d"] - df["hr_baseline"]
    return df


def env_features(env: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    env = env.sort_values(["user_key", "date"])
    out = env.groupby(["user_key", "date"], as_index=False).agg(temperature=("temperature", "mean"), humidity=("humidity", "mean"))
    out["temperature_mean_7d"] = out.groupby("user_key")["temperature"].transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
    out["temperature_min_7d"] = out.groupby("user_key")["temperature"].transform(lambda s: s.shift(1).rolling(window, min_periods=1).min())
    out["humidity_mean_7d"] = out.groupby("user_key")["humidity"].transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
    return out[["user_key", "date", "temperature_mean_7d", "temperature_min_7d", "humidity_mean_7d"]]


def symptom_features(daily: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    d = daily.sort_values(["user_key", "date"]).copy()
    for c in ["daily_day_symp", "daily_night_symp", "daily_limit_activity"]:
        d[c] = d[c].astype(str).str.lower().map({"true": 1.0, "false": 0.0}).fillna(d[c] if d[c].dtype == float else np.nan) if d[c].dtype == object else d[c]
        d[c + "_days_7d"] = d.groupby("user_key")[c].transform(lambda s: s.shift(1).rolling(window, min_periods=1).sum())
    return d[["user_key", "date", "daily_day_symp_days_7d", "daily_night_symp_days_7d", "daily_limit_activity_days_7d", "daily_day_symp", "daily_night_symp", "daily_limit_activity"]]


RELIEVER_MAP = {0: 0, 1: 1, 2: 1.5, 3: 3.5, 5: 6.5, 9: 10.5, 12: 13.0}  # ordinal range midpoints; category kept too


def medication_features(daily: pd.DataFrame, inhaler: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    d = daily.sort_values(["user_key", "date"]).copy()
    d["daily_relief_inhaler"] = pd.to_numeric(d["daily_relief_inhaler"], errors="coerce")
    d["reliever_days_7d"] = d.groupby("user_key")["daily_relief_inhaler"].transform(
        lambda s: s.shift(1).rolling(window, min_periods=1).apply(lambda x: (x > 0).sum()))
    same_day = d[["user_key", "date", "daily_relief_inhaler", "daily_prev_inhaler"]].copy()
    return same_day.merge(d[["user_key", "date", "reliever_days_7d"]], on=["user_key", "date"])


def trigger_encoding(daily: pd.DataFrame, top_k: int = 5) -> tuple[pd.DataFrame, list]:
    """Top-k one-hot per trigger ID + 'unknown' bucket. Vocabulary must be fit on TRAIN only;
    here we expose a function that accepts a pre-fitted vocabulary."""
    raise NotImplementedError  # use encode_triggers(daily, vocab)


def encode_triggers(daily: pd.DataFrame, vocab: list[str] | None = None) -> tuple[pd.DataFrame, list]:
    d = daily.copy()
    ids = d["daily_triggers"].fillna("").astype(str).str.split(",")
    exploded = ids.explode().str.strip()
    if vocab is None:
        vocab = exploded.value_counts().head(5).index.tolist()
    for v in vocab:
        d[f"trigger_{v}"] = ids.apply(lambda lst: int(v in [x.strip() for x in lst]))
    d["trigger_unknown"] = ids.apply(lambda lst: int(any(x.strip() not in vocab for x in lst if x.strip() != "")))
    cols = [f"trigger_{v}" for v in vocab] + ["trigger_unknown"]
    return d[["user_key", "date"] + cols], vocab
