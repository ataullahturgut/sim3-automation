import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


MODULE = Path(__file__).parents[1] / "v149_thesis" / "run_rich_short_horizon.py"
spec = importlib.util.spec_from_file_location("rich", MODULE)
rich = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rich)


def synthetic_panel(n=230):
    rng = np.random.default_rng(20260911)
    ret = rng.normal(0.0002, 0.01, n)
    close = 1900 * np.exp(np.cumsum(ret))
    d = pd.DataFrame({"date": pd.bdate_range("2023-01-02", periods=n), "close": close})
    for k in [1, 2, 3]:
        d[f"gold_ret_lag{k}"] = pd.Series(ret).shift(k - 1)
    for k in [3, 5, 10, 20]:
        d[f"gold_mom{k}"] = np.log(d.close / d.close.shift(k))
    for k in [5, 10, 20]:
        d[f"gold_rv{k}"] = pd.Series(ret).rolling(k).std(ddof=0)
    return d


def test_three_day_target_matures_only_after_three_origins():
    d = synthetic_panel()
    paths, y, _ = rich.raw_paths(d, 3, rich.B0, end=190)
    for t in range(120, 190):
        selected = rich.prior_best(paths, y, t, 3)
        if selected:
            assert all(j + 3 <= t for j in selected[2])


def test_prefix_invariance_for_raw_predictions():
    d = synthetic_panel()
    full, _, _ = rich.raw_paths(d, 1, rich.B0, end=200)
    prefix, _, _ = rich.raw_paths(d.iloc[:200].copy(), 1, rich.B0)
    assert full == prefix


def test_deterministic_replay():
    d = synthetic_panel()
    a = rich.replay(d, 1, rich.B0, 185)
    b = rich.replay(d, 1, rich.B0, 185)
    pd.testing.assert_frame_equal(a, b)


def test_empty_metrics_fail_closed():
    assert rich.metrics(pd.DataFrame())["status"] == "BLOCKED_INSUFFICIENT_COMPLETE_CASE"
