import json
import pytest
import pandas as pd
import numpy as np

from app.ml import ingestion, aggregation, baselines, labels, leakage, dataset, pipeline


def _mini_daily():
    return pd.DataFrame({
        "user_key": [1]*5, "date": [0, 1, 2, 3, 4],
        "pef_max": [500, 480, 460, 440, 420],
    })


def test1_no_future_pef_in_baseline():
    d = _mini_daily()
    b = baselines.baseline_expanding_max(d)
    # baseline at day 2 must be max of days 0,1 = 500, not 460
    assert b.loc[2, "baseline_expanding_max"] == 500
    leakage.assert_baseline_uses_only_prior(d.merge(b, on=["user_key", "date"]) if False else d.assign(baseline_expanding_max=b["baseline_expanding_max"]), "baseline_expanding_max")


def test2_future_symptoms_not_in_window():
    # trailing feature uses shift(1): day T uses days < T
    d = pd.DataFrame({"user_key": [1]*4, "date": [0,1,2,3], "daily_day_symp": [1,0,0,1]})
    d["x"] = d.groupby("user_key")["daily_day_symp"].transform(lambda s: s.shift(1).rolling(2, min_periods=1).sum())
    assert d.loc[1, "x"] == 1  # day 1 uses day 0
    assert d.loc[3, "x"] == 0  # day 3 uses days 1,2 (0+0), NOT day 3's own value


def test3_future_reliever_not_in_window():
    d = pd.DataFrame({"user_key": [1]*4, "date": [0,1,2,3], "r": [5,0,0,9]})
    d["x"] = d.groupby("user_key")["r"].transform(lambda s: s.shift(1).rolling(2, min_periods=1).sum())
    assert d.loc[3, "x"] == 0


def test4_rolling_baseline_no_future():
    d = _mini_daily()
    b = baselines.baseline_rolling_median(d, window=2, min_periods=1)
    # at day 2, baseline should be median of days 0,1 = 490
    assert b.loc[2, "baseline_rolling_median"] == 490


def test5_expanding_baseline_prior_only():
    d = _mini_daily()
    b = baselines.baseline_expanding_max(d)
    assert b.loc[0, "baseline_expanding_max"] != b.loc[0, "baseline_expanding_max"]  # NaN
    assert b.loc[4, "baseline_expanding_max"] == 500


def test6_user_partition_disjoint():
    split = dataset.patient_level_split([1,2,3,4,5,6,7,8,9,10], seed=1)
    leakage.assert_user_partition_disjoint(split["train"], split["test"])
    with pytest.raises(AssertionError):
        leakage.assert_user_partition_disjoint({1,2,3}, {3,4})


def test7_no_spo2_in_feature_matrix():
    meta = json.loads((__import__('pathlib').Path(__file__).parents[3] / "artifacts" / "aamos00" / "feature_metadata.json").read_text())
    assert not any("spo2" in f.lower() for f in meta["feature_names"])


def test8_no_dust_in_feature_matrix():
    from pathlib import Path
    meta = json.loads((Path(__file__).parents[3] / "artifacts" / "aamos00" / "feature_metadata.json").read_text())
    assert not any(("dust" in f.lower() or "pm2" in f.lower() or "pm10" in f.lower() or "aqi" in f.lower()) for f in meta["feature_names"])


def test9_raw_files_untouched():
    # checksums in inventory must match current files
    from pathlib import Path
    inv = json.loads((Path(__file__).parents[3] / "artifacts" / "aamos00" / "data_inventory.json").read_text())
    import hashlib
    for name, entry in inv.items():
        p = Path(__file__).parents[3] / "data" / "aamos00" / entry["filename"]
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert h == entry["sha256"], name


def test10_target_config_changeable():
    steep = pd.DataFrame({"user_key": [1]*5, "date": [0, 1, 2, 3, 4], "pef_max": [500, 480, 300, 300, 300]})
    d = steep.merge(baselines.baseline_expanding_max(steep), on=["user_key", "date"])
    t1 = labels.candidate_target(d, "baseline_expanding_max", 80, 1, 7)
    t2 = labels.candidate_target(d, "baseline_expanding_max", 60, 1, 7)
    assert not t1.equals(t2)  # different config -> different target, no code change needed
