"""Load AAMOS-00 files and build a reproducible inventory."""
import hashlib
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "aamos00"

FILES = {
    "patient_info": "anonym_aamos00_patient_info.csv",
    "daily": "anonym_aamos00_dailyquestionnaire.csv",
    "weekly": "anonym_aamos00_weeklyquestionnaire.csv",
    "end": "anonym_aamos00_endquestionnaire.csv",
    "environment": "anonym_aamos00_environment.csv",
    "peakflow": "anonym_aamos00_peakflow.csv",
    "inhaler": "anonym_aamos00_smartinhaler.csv",
    "smartwatch1": "anonym_aamos00_smartwatch1.csv",
    "smartwatch2": "anonym_aamos00_smartwatch2.csv",
    "smartwatch3": "anonym_aamos00_smartwatch3.csv",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_table(name: str, nrows: int | None = None) -> pd.DataFrame:
    path = DATA_DIR / FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"Missing AAMOS-00 file: {path}")
    return pd.read_csv(path, nrows=nrows)


def build_inventory(out_path: Path, nrows: int | None = None) -> dict:
    inventory = {}
    for name, fname in FILES.items():
        path = DATA_DIR / fname
        df = pd.read_csv(path, nrows=nrows)
        entry = {
            "filename": fname,
            "sha256": _sha256(path),
            "row_count": int(len(df)),
            "columns": list(df.columns),
            "participants": int(df["user_key"].nunique()) if "user_key" in df else None,
            "date_min": int(df["date"].min()) if "date" in df.columns else None,
            "date_max": int(df["date"].max()) if "date" in df.columns else None,
            "missingness": {c: round(float(df[c].isna().mean()), 4) for c in df.columns},
        }
        inventory[name] = entry
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return inventory
