"""Schema validation for AAMOS-00. Fails loudly on structural errors."""
import pandas as pd

SCHEMAS = {
    "patient_info": {"required": ["user_key", "sex", "age_range", "pef_best", "max_pef_expected"],
                      "dtypes": {"user_key": "integer"}},
    "daily": {"required": ["user_key", "date", "daily_night_symp", "daily_day_symp", "daily_limit_activity", "daily_prev_inhaler", "daily_relief_inhaler", "daily_triggers"]},
    "weekly": {"required": ["user_key", "date", "weekly_night_symp", "weekly_hospital", "weekly_er", "weekly_doc", "weekly_oral"]},
    "environment": {"required": ["user_key", "date", "temperature", "humidity"]},
    "peakflow": {"required": ["user_key", "date", "hour", "pef_max", "pefs", "morning"]},
    "inhaler": {"required": ["user_key", "date", "hour", "name"]},
    "smartwatch": {"required": ["user_key", "date", "time", "activity_type", "intensity", "steps", "hr"]},
}

NUMERIC_RANGES = {
    "pef_max": (0, 900),
    "temperature": (-40, 60),
    "humidity": (0, 100),
    "hr": (20, 250),
}


def validate_table(name: str, df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    schema = SCHEMAS.get(name, {})
    for col in schema.get("required", []):
        if col not in df.columns:
            errors.append(f"missing required column: {col}")
    if errors:
        return {"table": name, "errors": errors, "warnings": warnings}

    if "user_key" in df and df["user_key"].isna().any():
        errors.append("null user_key")
    if "date" in df:
        if df["date"].isna().any():
            errors.append("null date")
        if (df["date"] < 0).any() or (df["date"] > 400).any():
            errors.append("date outside expected range 0..400")
    for col, (lo, hi) in NUMERIC_RANGES.items():
        if col in df:
            bad = df[col].dropna()
            if ((bad < lo) | (bad > hi)).any():
                errors.append(f"{col} out of range [{lo},{hi}]")
    dupes = df.duplicated().sum()
    if dupes:
        warnings.append(f"{int(dupes)} full duplicate rows")
    missing = {c: round(float(df[c].isna().mean()), 4) for c in df.columns}
    return {"table": name, "errors": errors, "warnings": warnings, "missingness": missing,
            "rows": int(len(df)), "participants": int(df["user_key"].nunique()) if "user_key" in df else None}


def validate_all(tables: dict[str, pd.DataFrame]) -> dict:
    report = {}
    for name, df in tables.items():
        key = name if name in SCHEMAS else ("smartwatch" if name.startswith("smartwatch") else name)
        report[name] = validate_table(key, df)
    all_errors = [e for r in report.values() for e in r["errors"]]
    report["_summary"] = {"passed": len(all_errors) == 0, "error_count": len(all_errors)}
    return report
