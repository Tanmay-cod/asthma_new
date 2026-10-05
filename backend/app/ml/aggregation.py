"""Daily PEF aggregation: one row per user_key + date."""
import pandas as pd


def build_daily_pef(peakflow: pd.DataFrame) -> pd.DataFrame:
    """pef_max is already the best of three blows per session.
    Aggregation rule: for a user/day, take max(pef_max) as the daily best PEF;
    count sessions; keep 'morning' True if any session was morning.
    No future information is used (per-day aggregation only)."""
    df = peakflow.copy()
    daily = (df.groupby(["user_key", "date"], as_index=False)
               .agg(pef_max=("pef_max", "max"),
                    morning=("morning", "max"),
                    pef_measurement_count=("pef_max", "size")))
    return daily.sort_values(["user_key", "date"]).reset_index(drop=True)
