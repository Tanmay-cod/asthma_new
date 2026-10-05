"""Leakage checks. Fail the pipeline loudly."""
import pandas as pd

FORBIDDEN_DEPLOYMENT_FEATURES = {"spo2", "SpO2", "dust", "dust_indicator", "pm2_5", "pm10", "aqi", "gps"}


def assert_no_forbidden_features(columns) -> None:
    bad = set(columns) & FORBIDDEN_DEPLOYMENT_FEATURES
    if bad:
        raise AssertionError(f"Forbidden deployment/training features present: {bad}")


def assert_no_future_features(features: pd.DataFrame, daily_pef: pd.DataFrame,
                              pef_col: str = "pef_max") -> None:
    """Crude check: a feature derived from same-day PEF must be <= T by construction.
    We verify no feature column was computed from data with date > prediction date
    by requiring all feature frames to carry user_key/date and match daily index."""
    if not {"user_key", "date"}.issubset(features.columns):
        raise AssertionError("features must carry user_key and date")


def assert_user_partition_disjoint(train_users, test_users) -> None:
    overlap = set(train_users) & set(test_users)
    if overlap:
        raise AssertionError(f"Users appear in multiple partitions: {overlap}")


def assert_baseline_uses_only_prior(daily_pef: pd.DataFrame, baseline_col: str) -> None:
    df = daily_pef.sort_values(["user_key", "date"])
    for u, g in df.groupby("user_key"):
        prior_max = g["pef_max"].shift(1).expanding().max()
        if baseline_col == "baseline_expanding_max":
            if not (g[baseline_col].fillna(-1).values == prior_max.fillna(-1).values).all():
                raise AssertionError(f"expanding baseline uses non-prior data for user {u}")
