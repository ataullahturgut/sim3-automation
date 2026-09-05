from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "tools" / "replay_macro_event_successor_v1_score.py"
spec = importlib.util.spec_from_file_location("replay_macro_event_successor_v1_score", MOD_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def make_panel(n=26):
    rows=[]
    for i in range(n):
        year=2016 + i // 12
        month=i % 12 + 1
        ref=f"{year:04d}-{month:02d}"
        rows.append({
            "reference_month": ref,
            "release_ts": datetime(year, month, min(5, 28), 13, 30, tzinfo=timezone.utc),
            "actual": {
                "nfp": 100.0 + (i % 5) * 10.0,
                "unemployment": 4.0 + (i % 3) * 0.1,
                "ahe_mom": 0.2 + (i % 4) * 0.1,
            },
            "consensus": {
                "nfp": 95.0,
                "unemployment": 4.1,
                "ahe_mom": 0.3,
            },
        })
    return rows


def test_first_24_rows_are_warmup():
    out=mod.replay(make_panel())
    assert all(x["state"]=="INSUFFICIENT_HISTORY" for x in out[:24])
    assert out[24]["macro_gold_score"] is not None


def test_gold_orientation_formula():
    prior={"nfp":[-1.0,1.0]*12,"unemployment":[-0.1,0.1]*12,"ahe_mom":[-0.1,0.1]*12}
    sigmas={k:mod.sample_sigma(v) for k,v in prior.items()}
    # Positive NFP and AHE surprises are adverse; positive unemployment surprise is supportive.
    components=[-(1.0/sigmas["nfp"]),(0.1/sigmas["unemployment"]),-(0.1/sigmas["ahe_mom"])]
    assert components[0] < 0
    assert components[1] > 0
    assert components[2] < 0


def test_window_mapping():
    assert mod.evidence_window("2020-12")=="DEV"
    assert mod.evidence_window("2021-01")=="VAL"
    assert mod.evidence_window("2024-01")=="LOCK"


def test_context_month_uses_release_month():
    dt=datetime(2026,9,4,12,30,tzinfo=timezone.utc)
    assert mod.context_month(dt)=="2026-09"
