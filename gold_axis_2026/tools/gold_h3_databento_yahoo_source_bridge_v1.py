from __future__ import annotations

import io
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUTJ = AX / "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_2026-10-05.json"
OUTM = AX / "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_2026-10-05.md"
OUTC = AX / "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_CHANNEL_METRICS_2026-10-05.csv"

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1h"
ROOTS = ["GC", "SI", "NQ", "ZN", "CL"]
ROLLS = ["c", "n", "v"]
BRIDGE_START = "2025-01-02"
BRIDGE_END = "2026-10-03"
MAX_APPROVED_COST_USD = 1.60

FROZEN_REF = "origin/gold-h3-llrs-v1-20261004"
FROZEN_PATH = "gold_axis_2026/GOLD_H3_LLRS_V1_HOURLY_PANEL_2026-10-04.csv"

def load_frozen():
    subprocess.run(
        ["git", "fetch", "origin", "gold-h3-llrs-v1-20261004:refs/remotes/origin/gold-h3-llrs-v1-20261004"],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=120
    )
    p = subprocess.run(
        ["git", "show", f"{FROZEN_REF}:{FROZEN_PATH}"],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=120
    )
    z = pd.read_csv(io.StringIO(p.stdout))
    z["ts"] = pd.to_datetime(z["ts"], utc=True)
    return z.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)

def yahoo_fetch(symbol):
    p1 = int(pd.Timestamp(BRIDGE_START, tz="UTC").timestamp())
    p2 = int(pd.Timestamp(BRIDGE_END, tz="UTC").timestamp())
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 academic research"})
    last = None
    for host in ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]:
        url = f"https://{host}/v8/finance/chart/{requests.utils.quote(symbol, safe='')}"
        params = {"period1": p1, "period2": p2, "interval": "1h", "events": "history", "includeAdjustedClose": "true"}
        try:
            r = s.get(url, params=params, timeout=60)
            if r.status_code != 200:
                last = f"HTTP {r.status_code}"
                continue
            j = r.json()["chart"]
            if j.get("error") or not j.get("result"):
                last = f"chart_error={j.get('error')}"
                continue
            x = j["result"][0]
            q = x["indicators"]["quote"][0]
            rows = []
            for i, t in enumerate(x.get("timestamp", [])):
                c = q.get("close", [])[i]
                v = q.get("volume", [None] * len(x.get("timestamp", [])))[i]
                if c is None:
                    continue
                rows.append((pd.to_datetime(t, unit="s", utc=True), float(c), np.nan if v is None else float(v)))
            return pd.DataFrame(rows, columns=["ts", "close", "volume"]).drop_duplicates("ts").sort_values("ts")
        except Exception as e:
            last = repr(e)
    raise RuntimeError(f"Yahoo fetch failed {symbol}: {last}")

def databento_all(client):
    symbols = [f"{r}.{roll}.0" for r in ROOTS for roll in ROLLS]
    est = float(client.metadata.get_cost(
        dataset=DATASET, schema=SCHEMA, symbols=symbols, stype_in="continuous",
        start=BRIDGE_START, end=BRIDGE_END
    ))
    if est > MAX_APPROVED_COST_USD:
        raise RuntimeError(f"ESTIMATED_COST_EXCEEDS_APPROVAL:{est:.6f}>{MAX_APPROVED_COST_USD:.2f}")
    data = client.timeseries.get_range(
        dataset=DATASET, schema=SCHEMA, symbols=symbols, stype_in="continuous",
        start=BRIDGE_START, end=BRIDGE_END
    )
    d = data.to_df().reset_index()
    if "ts_event" not in d.columns:
        if "index" in d.columns:
            d = d.rename(columns={"index": "ts_event"})
        else:
            raise RuntimeError(f"NO_TS_EVENT columns={list(d.columns)}")
    d["ts"] = pd.to_datetime(d["ts_event"], utc=True)
    if "symbol" not in d.columns:
        raise RuntimeError(f"NO_SYMBOL_COLUMN columns={list(d.columns)}")
    d["symbol"] = d["symbol"].astype(str)
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d["volume"] = pd.to_numeric(d.get("volume"), errors="coerce")
    d = d[np.isfinite(d.close) & (d.close > 0)].copy()
    return d[["ts", "symbol", "instrument_id", "close", "volume"]], est

def ret_metrics(y, d, h):
    z = y.merge(d, on="ts", how="inner", suffixes=("_y", "_d")).sort_values("ts")
    if len(z) < h + 50:
        return {"n": int(len(z)), "corr": None, "sign": None, "mae_bps": None}
    ry = np.log(z.close_y.astype(float)).diff(h)
    rd = np.log(z.close_d.astype(float)).diff(h)
    q = pd.DataFrame({"ry": ry, "rd": rd}).dropna()
    if len(q) < 50:
        return {"n": int(len(q)), "corr": None, "sign": None, "mae_bps": None}
    corr = float(q.ry.corr(q.rd))
    sign = float((np.sign(q.ry) == np.sign(q.rd)).mean())
    mae = float(np.mean(np.abs(q.ry - q.rd)) * 10000.0)
    return {"n": int(len(q)), "corr": corr, "sign": sign, "mae_bps": mae}

def compare_channel(root, roll, frozen, dbdf, yahoo_live):
    sym = f"{root}.{roll}.0"
    d = dbdf[dbdf.symbol == sym][["ts", "close", "volume", "instrument_id"]].copy()
    y = frozen[["ts", root]].rename(columns={root: "close"}).dropna().copy()

    aligned = y.merge(d[["ts", "close"]], on="ts", how="inner", suffixes=("_y", "_d"))
    coverage = len(aligned) / max(len(y), 1)
    if len(aligned):
        ratio = aligned.close_d.astype(float) / aligned.close_y.astype(float)
        price_ratio_med = float(np.median(ratio))
        price_ratio_mad = float(np.median(np.abs(ratio - np.median(ratio))))
        level_corr = float(aligned.close_y.astype(float).corr(aligned.close_d.astype(float)))
    else:
        price_ratio_med = price_ratio_mad = level_corr = None

    m1 = ret_metrics(y, d[["ts", "close"]], 1)
    m3 = ret_metrics(y, d[["ts", "close"]], 3)
    m6 = ret_metrics(y, d[["ts", "close"]], 6)

    vol_corr = vol_sign = vol_log_mae = None
    vol_n = 0
    if root in {"GC", "SI"} and yahoo_live is not None:
        zv = yahoo_live[["ts", "volume"]].merge(d[["ts", "volume"]], on="ts", suffixes=("_y", "_d")).dropna()
        zv = zv[(zv.volume_y > 0) & (zv.volume_d > 0)].copy()
        vol_n = int(len(zv))
        if vol_n >= 50:
            ly = np.log1p(zv.volume_y.astype(float))
            ld = np.log1p(zv.volume_d.astype(float))
            vol_corr = float(ly.corr(ld))
            vol_sign = float((np.sign(ly.diff()) == np.sign(ld.diff())).dropna().mean())
            vol_log_mae = float(np.mean(np.abs(ly - ld)))

    # Deterministic source-agreement score. No outcome labels.
    # Correlation and sign dominate; return MAE and coverage break ties.
    vals = [m1["corr"], m3["corr"], m6["corr"], m1["sign"], m3["sign"], m6["sign"]]
    if any(v is None or not np.isfinite(v) for v in vals):
        score = -999.0
    else:
        score = (
            0.22*m1["corr"] + 0.18*m3["corr"] + 0.14*m6["corr"] +
            0.16*m1["sign"] + 0.12*m3["sign"] + 0.08*m6["sign"] +
            0.10*coverage -
            0.0005*min(m1["mae_bps"] or 9999.0, 500.0)
        )
        if root in {"GC", "SI"} and vol_corr is not None:
            score += 0.05*vol_corr

    return {
        "root": root, "roll": roll, "symbol": sym,
        "yahoo_frozen_n": int(len(y)), "databento_n": int(len(d)),
        "aligned_n": int(len(aligned)), "coverage": float(coverage),
        "level_corr": level_corr,
        "price_ratio_median": price_ratio_med, "price_ratio_mad": price_ratio_mad,
        "r1_corr": m1["corr"], "r1_sign": m1["sign"], "r1_mae_bps": m1["mae_bps"],
        "r3_corr": m3["corr"], "r3_sign": m3["sign"], "r3_mae_bps": m3["mae_bps"],
        "r6_corr": m6["corr"], "r6_sign": m6["sign"], "r6_mae_bps": m6["mae_bps"],
        "volume_n": vol_n, "volume_log_corr": vol_corr,
        "volume_change_sign": vol_sign, "volume_log_mae": vol_log_mae,
        "source_agreement_score": float(score),
    }

def main():
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db

    frozen = load_frozen()
    client = db.Historical(key)
    dbdf, est = databento_all(client)

    yahoo_live = {}
    for root in ["GC", "SI"]:
        try:
            yahoo_live[root] = yahoo_fetch(f"{root}=F")
        except Exception:
            yahoo_live[root] = None

    rows = []
    for root in ROOTS:
        for roll in ROLLS:
            rows.append(compare_channel(root, roll, frozen, dbdf, yahoo_live.get(root)))
    m = pd.DataFrame(rows)
    m.to_csv(OUTC, index=False)

    winners = {}
    for root, g in m.groupby("root", sort=False):
        gg = g.sort_values(
            ["source_agreement_score", "r1_corr", "r1_sign", "r1_mae_bps"],
            ascending=[False, False, False, True]
        )
        b = gg.iloc[0]
        winners[root] = {
            "roll": str(b.roll),
            "symbol": str(b.symbol),
            "score": float(b.source_agreement_score),
            "r1_corr": float(b.r1_corr),
            "r1_sign": float(b.r1_sign),
            "r1_mae_bps": float(b.r1_mae_bps),
            "r3_corr": float(b.r3_corr),
            "r6_corr": float(b.r6_corr),
            "coverage": float(b.coverage),
            "volume_log_corr": None if pd.isna(b.volume_log_corr) else float(b.volume_log_corr),
        }

    # Conservative pass gate for a historical source bridge.
    gates = {}
    all_pass = True
    for root, w in winners.items():
        ok = (
            w["coverage"] >= 0.97 and
            w["r1_corr"] >= 0.995 and
            w["r1_sign"] >= 0.985 and
            w["r1_mae_bps"] <= 1.50 and
            w["r3_corr"] >= 0.995 and
            w["r6_corr"] >= 0.995
        )
        if root in {"GC", "SI"} and w["volume_log_corr"] is not None:
            ok = ok and w["volume_log_corr"] >= 0.98
        gates[root] = bool(ok)
        all_pass = all_pass and bool(ok)

    out = {
        "schema": "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_V1",
        "date": "2026-10-05",
        "dataset": DATASET,
        "schema_data": SCHEMA,
        "bridge_window": [BRIDGE_START, BRIDGE_END],
        "estimated_cost_usd_before_download": est,
        "approved_cost_ceiling_usd": MAX_APPROVED_COST_USD,
        "raw_vendor_values_committed": False,
        "selection_uses_dptc_outcomes": False,
        "frozen_yahoo_rows": int(len(frozen)),
        "databento_rows_in_memory": int(len(dbdf)),
        "winners": winners,
        "gates": gates,
        "all_channels_strict_bridge_pass": bool(all_pass),
        "status": "STRICT_SOURCE_BRIDGE_PASS" if all_pass else "SOURCE_BRIDGE_REQUIRES_REVIEW",
        "next_action": (
            "Fetch 2023-2024 only for the frozen per-channel winning roll rules and replay LLRS/IFBC/DPTC unchanged."
            if all_pass else
            "Inspect channel-level mismatches; do not fetch/replay 2023-2024 as exact lineage yet."
        ),
    }
    OUTJ.write_text(json.dumps(out, indent=2, default=str) + "\n", encoding="utf-8")

    lines = [
        "# GOLD H3 — Databento ↔ Frozen Yahoo Source Bridge — 2026-10-05", "",
        f"**Status:** **{out['status']}**  ",
        f"Pre-download estimated Databento cost: **USD {est:.4f}** (approved ceiling USD {MAX_APPROVED_COST_USD:.2f}).  ",
        "**No raw Databento prices are committed. Roll selection uses source agreement only; no DPTC outcome labels.**", "",
        "## Per-channel roll comparison", "",
        "| Root | Roll | Coverage | r1 corr | r1 sign | r1 MAE bps | r3 corr | r6 corr | Vol log corr | Score |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in m.sort_values(["root", "source_agreement_score"], ascending=[True, False]).itertuples():
        vc = "—" if pd.isna(r.volume_log_corr) else f"{r.volume_log_corr:.5f}"
        lines.append(
            f"| {r.root} | {r.roll} | {100*r.coverage:.2f}% | {r.r1_corr:.6f} | {100*r.r1_sign:.3f}% | "
            f"{r.r1_mae_bps:.4f} | {r.r3_corr:.6f} | {r.r6_corr:.6f} | {vc} | {r.source_agreement_score:.6f} |"
        )
    lines += ["", "## Frozen source mapping", "",
              "| Root | Winner | Strict gate | r1 corr | r1 sign | MAE bps | Coverage |",
              "|---|---|---|---:|---:|---:|---:|"]
    for root in ROOTS:
        w = winners[root]
        lines.append(
            f"| {root} | **{w['symbol']}** | **{gates[root]}** | {w['r1_corr']:.6f} | "
            f"{100*w['r1_sign']:.3f}% | {w['r1_mae_bps']:.4f} | {100*w['coverage']:.2f}% |"
        )
    lines += ["", "## Governance", "",
              "- This bridge is source-only and does not inspect RESCUE/BROKEN, DPTC Q95/Q99, or forecast correctness.",
              "- The selected roll rule may differ by product.",
              "- 2023–2024 replay is allowed only if the bridge quality is scientifically adequate; otherwise it remains a proxy reconstruction.",
              "- No LLRS/IFBC/DPTC thresholds or architecture were changed."]
    OUTM.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUTM.read_text())

if __name__ == "__main__":
    main()
