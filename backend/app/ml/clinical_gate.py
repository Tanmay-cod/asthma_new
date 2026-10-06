"""Clinical target approval gate. Training must not start while pending."""
import yaml
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "docs" / "clinical_target_schema.yaml"

REQUIRED_KEYS = {"threshold_pct", "consecutive_days", "baseline_method", "prediction_horizon_days"}


def load_schema(path: Path | None = None) -> dict:
    return yaml.safe_load((path or SCHEMA_PATH).read_text(encoding="utf-8"))


def training_allowed(schema: dict) -> bool:
    """True only if status is approved AND all clinical fields are filled AND valid."""
    if schema.get("status") != "approved":
        return False
    t = schema.get("target", {})
    if not all(t.get(k) is not None for k in REQUIRED_KEYS):
        return False
    try:
        if not (0 < t["threshold_pct"] <= 100):
            return False
        if t["consecutive_days"] < 1 or t["prediction_horizon_days"] < 1:
            return False
        if t["baseline_method"] not in {"pef_best", "expanding_max", "rolling_median"}:
            return False
    except (TypeError, KeyError):
        return False
    if schema.get("clinical_outcome", {}).get("type") is None:
        return False
    return True


def assert_training_allowed() -> None:
    schema = load_schema()
    if not training_allowed(schema):
        raise RuntimeError("MODEL TRAINING BLOCKED — AWAITING CLINICAL TARGET VALIDATION")
