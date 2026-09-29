from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import gold_monthly_f4_b1_transform_parity_v1 as b1
import gold_monthly_f4_all6_compact_candidate_v1 as core


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--external-v2", required=True)
    ap.add_argument("--b2-audit", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    bundle, smeta = snap.load_snapshot(a.snapshot)
    ext = json.loads(Path(a.external_v2).read_text())
    b2doc = json.loads(Path(a.b2_audit).read_text())

    if not b2doc.get("gates", {}).get("pass"):
        raise RuntimeError("B2_AUTHORITY_NOT_PASS")
    if ext.get("payload_sha256") != b2doc.get("authority", {}).get("external_v2_payload_sha256"):
        raise RuntimeError("EXTERNAL_V2_PAYLOAD_MISMATCH")

    cfg = core.configure(22, 66)
    series = core.build_series(ext)
    rows = []

    for t in base.month_range(a.start, a.end):
        samples = core.all6_samples(bundle, t, series)
        keys = sorted(k for k in samples if k < t)
        if not keys or keys[0] != "2010-03":
            raise RuntimeError(f"HISTORY_PARITY_FAIL {t}")
        p, n, diag = anfis.select(samples, t, "CHHHO")
        o = base.month_shift(t, -1)
        forecast = float(bundle.core_gold[o] * math.exp(float(p[0])))
        actual = float(bundle.core_gold[t])
        if not np.isfinite(forecast):
            raise RuntimeError(f"NONFINITE_FORECAST {t}")
        rows.append({
            "target": t,
            "origin": o,
            "variant": "ALL6",
            "input_dimension": 22,
            "population": 66,
            "train_rows": n,
            "diag": diag,
            "pred_log_return_gold": float(p[0]),
            "forecast": forecast,
            "actual": actual,
            "rw": float(bundle.core_gold[o]),
            "abs_error": abs(forecast-actual),
            "signed_error": forecast-actual,
        })

    out = {
        "schema":"GOLD_MONTHLY_F4_ALL6_COMPACT_SHARD_V1_2026-09-29",
        "label":a.label,
        "start":a.start,
        "end":a.end,
        "optimizer":cfg,
        "authority":{
            "selection_period":"2022-04..2024-12",
            "2025_used":False,
            "2026_used":False,
            "random_split":"NONE",
            "snapshot_payload_sha256":smeta["payload_sha256"],
            "external_v2_payload_sha256":ext["payload_sha256"],
            "b2_gate_schema":b2doc.get("schema"),
            "parallelization_semantics":"OUTER_ORIGINS_INDEPENDENT__SEED_DEPENDS_ON_TARGET__NO_CROSS_ORIGIN_STATE",
            "neon_reads":0,
        },
        "rows":rows,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_ALL6_SHARD_GATE=PASS")
    print(json.dumps({"label":a.label,"start":a.start,"end":a.end,"n":len(rows),
                      "targets":[r["target"] for r in rows]},sort_keys=True))


if __name__ == "__main__":
    main()
