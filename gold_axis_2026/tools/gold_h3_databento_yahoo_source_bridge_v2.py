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
OUTJ = AX / "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_V2_2026-10-05.json"
OUTM = AX / "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_V2_2026-10-05.md"
OUTC = AX / "GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_V2_CHANNEL_METRICS_2026-10-05.csv"

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1h"
ROOTS = ["GC", "SI", "NQ", "ZN", "CL"]
ROLLS = ["c", "n", "v"]
BRIDGE_START = "2025-01-02"
BRIDGE_END = "2026-10-03"
MAX_ADDITIONAL_COST_USD = 1.60
ROLL_EXCLUSION_HOURS = 30

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
            tslist = x.get("timestamp", [])
            close = q.get("close", [])
            volume = q.get("volume", [None] * len(tslist))
            for i, t in enumerate(tslist):
                c = close[i]
                if c is None:
                    continue
                v = volume[i] if i < len(volume) else None
                rows.append((pd.to_datetime(t, unit="s", utc=True), float(c), np.nan if v is None else float(v)))
            return pd.DataFrame(rows, columns=["ts", "close", "volume"]).drop_duplicates("ts").sort_values("ts")
        except Exception as e:
            last = repr(e)
    raise RuntimeError(f"Yahoo fetch failed {symbol}: {last}")

def fetch_roll_group(client, roll):
    symbols = [f"{r}.{roll}.0" for r in ROOTS]
    data = client.timeseries.get_range(
        dataset=DATASET, schema=SCHEMA, symbols=symbols, stype_in="continuous",
        start=BRIDGE_START, end=BRIDGE_END
    )
    d = data.to_df().reset_index()
    if "ts_event" not in d.columns:
        if "index" in d.columns:
            d = d.rename(columns={"index": "ts_event"})
        else:
            raise RuntimeError(f"NO_TS_EVENT roll={roll} columns={list(d.columns)}")
    if "symbol" not in d.columns:
        raise RuntimeError(f"NO_SYMBOL roll={roll} columns={list(d.columns)}")
    d["ts"] = pd.to_datetime(d["ts_event"], utc=True)
    d["symbol"] = d["symbol"].astype(str)
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d["volume"] = pd.to_numeric(d["volume"], errors="coerce")
    d = d[np.isfinite(d.close) & (d.close > 0)].copy()
    return d[["ts", "symbol", "instrument_id", "close", "volume"]]

def roll_exclusion_mask(d):
    q = d.sort_values("ts").copy()
    changed = q.instrument_id.ne(q.instrument_id.shift(1))
    roll_ts = list(q.loc[changed & q.instrument_id.shift(1).notna(), "ts"])
    bad = pd.Series(False, index=q.index)
    for rt in roll_ts:
        bad |= (q.ts >= rt - pd.Timedelta(hours=ROLL_EXCLUSION_HOURS)) & (q.ts <= rt + pd.Timedelta(hours=ROLL_EXCLUSION_HOURS))
    return q, bad, roll_ts

def pair_returns(y, d, h=1, nonroll=False):
    z = y.merge(d[["ts", "close", "nonroll_ok"]], on="ts", how="inner", suffixes=("_y", "_d")).sort_values("ts")
    z["ry"] = np.log(z.close_y.astype(float)).diff(h)
    z["rd"] = np.log(z.close_d.astype(float)).diff(h)
    if nonroll:
        ok = z.nonroll_ok.astype(bool)
        for k in range(1, h+1):
            ok &= z.nonroll_ok.shift(k).fillna(False).astype(bool)
        z = z[ok]
    q = z.dropna(subset=["ry", "rd"])
    if len(q) < 30:
        return {"n": int(len(q)), "corr": None, "sign": None, "mae_bps": None, "p99_bps": None}
    diff = np.abs(q.ry - q.rd) * 10000.0
    return {
        "n": int(len(q)),
        "corr": float(q.ry.corr(q.rd)),
        "sign": float((np.sign(q.ry) == np.sign(q.rd)).mean()),
        "mae_bps": float(diff.mean()),
        "p99_bps": float(diff.quantile(.99)),
    }

def compare(root, roll, frozen, group, yahoo_live):
    symbol = f"{root}.{roll}.0"
    d = group[group.symbol == symbol][["ts", "close", "volume", "instrument_id"]].copy().sort_values("ts")
    d, bad, roll_ts = roll_exclusion_mask(d)
    d["nonroll_ok"] = ~bad

    y = frozen[["ts", root]].rename(columns={root: "close"}).dropna().copy()
    z = y.merge(d[["ts", "close", "nonroll_ok"]], on="ts", how="inner", suffixes=("_y", "_d")).sort_values("ts")
    coverage = len(z) / max(len(y), 1)

    ratio = z.close_d.astype(float) / z.close_y.astype(float) if len(z) else pd.Series(dtype=float)
    exact_rel = np.abs(ratio - 1.0)
    near_price = float((exact_rel <= 1e-6).mean()) if len(z) else None
    nonroll = z[z.nonroll_ok.astype(bool)].copy()
    nr_ratio = nonroll.close_d.astype(float) / nonroll.close_y.astype(float) if len(nonroll) else pd.Series(dtype=float)
    nr_near_price = float((np.abs(nr_ratio - 1.0) <= 1e-6).mean()) if len(nonroll) else None

    full1 = pair_returns(y, d, 1, False)
    full3 = pair_returns(y, d, 3, False)
    full6 = pair_returns(y, d, 6, False)
    nr1 = pair_returns(y, d, 1, True)
    nr3 = pair_returns(y, d, 3, True)
    nr6 = pair_returns(y, d, 6, True)

    vol_n = 0
    vol_corr = vol_mae = nr_vol_corr = nr_vol_mae = None
    if root in {"GC", "SI"} and yahoo_live is not None:
        zv = yahoo_live[["ts", "volume"]].merge(d[["ts", "volume", "nonroll_ok"]], on="ts", suffixes=("_y", "_d")).dropna()
        zv = zv[(zv.volume_y > 0) & (zv.volume_d > 0)].copy()
        vol_n = int(len(zv))
        if vol_n >= 30:
            ly = np.log1p(zv.volume_y.astype(float)); ld = np.log1p(zv.volume_d.astype(float))
            vol_corr = float(ly.corr(ld)); vol_mae = float(np.mean(np.abs(ly-ld)))
            q = zv[zv.nonroll_ok.astype(bool)]
            if len(q) >= 30:
                ly2=np.log1p(q.volume_y.astype(float)); ld2=np.log1p(q.volume_d.astype(float))
                nr_vol_corr=float(ly2.corr(ld2)); nr_vol_mae=float(np.mean(np.abs(ly2-ld2)))

    # Selection score deliberately uses source agreement only.
    score = (
        0.20*(full1["corr"] if full1["corr"] is not None else -1) +
        0.15*(full3["corr"] if full3["corr"] is not None else -1) +
        0.10*(full6["corr"] if full6["corr"] is not None else -1) +
        0.15*(full1["sign"] if full1["sign"] is not None else 0) +
        0.10*coverage +
        0.15*(nr1["corr"] if nr1["corr"] is not None else -1) +
        0.10*(nr1["sign"] if nr1["sign"] is not None else 0) +
        0.05*(nr_near_price if nr_near_price is not None else 0) -
        0.0005*min(full1["mae_bps"] if full1["mae_bps"] is not None else 9999, 500)
    )
    if root in {"GC","SI"} and nr_vol_corr is not None:
        score += 0.04*nr_vol_corr

    return {
        "root": root, "roll": roll, "symbol": symbol,
        "yahoo_n": int(len(y)), "databento_n": int(len(d)), "aligned_n": int(len(z)),
        "coverage": float(coverage), "roll_count": int(len(roll_ts)),
        "near_price_share": near_price, "nonroll_near_price_share": nr_near_price,
        "r1_corr": full1["corr"], "r1_sign": full1["sign"], "r1_mae_bps": full1["mae_bps"], "r1_p99_bps": full1["p99_bps"],
        "r3_corr": full3["corr"], "r3_sign": full3["sign"], "r3_mae_bps": full3["mae_bps"],
        "r6_corr": full6["corr"], "r6_sign": full6["sign"], "r6_mae_bps": full6["mae_bps"],
        "nr_r1_corr": nr1["corr"], "nr_r1_sign": nr1["sign"], "nr_r1_mae_bps": nr1["mae_bps"], "nr_r1_p99_bps": nr1["p99_bps"],
        "nr_r3_corr": nr3["corr"], "nr_r3_sign": nr3["sign"], "nr_r3_mae_bps": nr3["mae_bps"],
        "nr_r6_corr": nr6["corr"], "nr_r6_sign": nr6["sign"], "nr_r6_mae_bps": nr6["mae_bps"],
        "volume_n": vol_n, "volume_log_corr": vol_corr, "volume_log_mae": vol_mae,
        "nr_volume_log_corr": nr_vol_corr, "nr_volume_log_mae": nr_vol_mae,
        "source_agreement_score": float(score),
    }

def main():
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client = db.Historical(key)

    # Cost-only guard before any V2 paid request.
    ests = {}
    for roll in ROLLS:
        symbols=[f"{r}.{roll}.0" for r in ROOTS]
        ests[roll]=float(client.metadata.get_cost(
            dataset=DATASET, schema=SCHEMA, symbols=symbols, stype_in="continuous",
            start=BRIDGE_START, end=BRIDGE_END
        ))
    total_est=float(sum(ests.values()))
    if total_est > MAX_ADDITIONAL_COST_USD:
        raise RuntimeError(f"V2_ESTIMATED_COST_EXCEEDS_APPROVAL:{total_est:.6f}>{MAX_ADDITIONAL_COST_USD:.2f}")

    frozen=load_frozen()
    groups={}
    for roll in ROLLS:
        groups[roll]=fetch_roll_group(client,roll)

    yahoo_live={}
    for root in ["GC","SI"]:
        try:
            yahoo_live[root]=yahoo_fetch(f"{root}=F")
        except Exception:
            yahoo_live[root]=None

    rows=[]
    for root in ROOTS:
        for roll in ROLLS:
            rows.append(compare(root,roll,frozen,groups[roll],yahoo_live.get(root)))
    m=pd.DataFrame(rows)
    m.to_csv(OUTC,index=False)

    winners={}
    for root,g in m.groupby("root",sort=False):
        gg=g.sort_values(["source_agreement_score","nr_r1_corr","r1_corr","coverage"],ascending=[False,False,False,False])
        b=gg.iloc[0]
        winners[root]={k:(None if pd.isna(b[k]) else (float(b[k]) if isinstance(b[k],(float,np.floating)) else int(b[k]) if isinstance(b[k],(int,np.integer)) else str(b[k])))
                       for k in ["roll","symbol","coverage","roll_count","near_price_share","nonroll_near_price_share",
                                 "r1_corr","r1_sign","r1_mae_bps","r3_corr","r6_corr",
                                 "nr_r1_corr","nr_r1_sign","nr_r1_mae_bps","nr_r3_corr","nr_r6_corr",
                                 "nr_volume_log_corr","source_agreement_score"]}

    gates={}
    for root,w in winners.items():
        # Acceptance focuses on exact source identity away from roll transitions,
        # while allowing Yahoo/Databento to differ at the roll handoff itself.
        ok=(
            w["coverage"] is not None and w["coverage"]>=0.97 and
            w["nonroll_near_price_share"] is not None and w["nonroll_near_price_share"]>=0.995 and
            w["nr_r1_corr"] is not None and w["nr_r1_corr"]>=0.999 and
            w["nr_r1_sign"] is not None and w["nr_r1_sign"]>=0.995 and
            w["nr_r1_mae_bps"] is not None and w["nr_r1_mae_bps"]<=0.25 and
            w["nr_r3_corr"] is not None and w["nr_r3_corr"]>=0.999 and
            w["nr_r6_corr"] is not None and w["nr_r6_corr"]>=0.999
        )
        if root in {"GC","SI"} and w["nr_volume_log_corr"] is not None:
            ok = ok and w["nr_volume_log_corr"]>=0.98
        gates[root]=bool(ok)

    all_pass=all(gates.values())
    out={
        "schema":"GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_V2",
        "date":"2026-10-05",
        "correction":"Separate c/n/v requests avoid alias deduplication from V1 combined request.",
        "dataset":DATASET,"schema_data":SCHEMA,
        "bridge_window":[BRIDGE_START,BRIDGE_END],
        "v2_estimated_cost_usd":total_est,
        "v2_cost_by_roll_usd":ests,
        "v2_cost_ceiling_usd":MAX_ADDITIONAL_COST_USD,
        "raw_vendor_values_committed":False,
        "selection_uses_dptc_outcomes":False,
        "roll_exclusion_hours":ROLL_EXCLUSION_HOURS,
        "winners":winners,"gates":gates,
        "all_channels_bridge_pass":bool(all_pass),
        "status":"SOURCE_BRIDGE_V2_PASS" if all_pass else "SOURCE_BRIDGE_V2_REQUIRES_REVIEW",
        "next_action":(
            "Freeze per-channel roll mapping; cost-check/fetch 2023-2024; rebuild LLRS/IFBC; replay DPTC unchanged."
            if all_pass else
            "Diagnose remaining source differences before calling 2023-2024 reconstruction exact."
        )
    }
    OUTJ.write_text(json.dumps(out,indent=2,default=str)+"\n",encoding="utf-8")

    lines=[
        "# GOLD H3 — Databento ↔ Frozen Yahoo Source Bridge V2 — 2026-10-05","",
        f"**Status:** **{out['status']}**  ",
        f"V2 estimated additional Databento cost: **USD {total_est:.4f}** (ceiling USD {MAX_ADDITIONAL_COST_USD:.2f}).  ",
        "V2 fixes V1 alias-deduplication by requesting each roll family separately.","",
        "## Full and non-roll source agreement","",
        "| Root | Roll | Cov | Full r1 corr | Full sign | Full MAE bps | Non-roll exact px | NR r1 corr | NR sign | NR MAE bps | NR r3 | NR r6 | NR vol corr | Score |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in m.sort_values(["root","source_agreement_score"],ascending=[True,False]).itertuples():
        vc="—" if pd.isna(r.nr_volume_log_corr) else f"{r.nr_volume_log_corr:.5f}"
        lines.append(
            f"| {r.root} | {r.roll} | {100*r.coverage:.2f}% | {r.r1_corr:.6f} | {100*r.r1_sign:.3f}% | {r.r1_mae_bps:.4f} | "
            f"{100*r.nonroll_near_price_share:.3f}% | {r.nr_r1_corr:.6f} | {100*r.nr_r1_sign:.3f}% | {r.nr_r1_mae_bps:.4f} | "
            f"{r.nr_r3_corr:.6f} | {r.nr_r6_corr:.6f} | {vc} | {r.source_agreement_score:.6f} |"
        )
    lines += ["","## Frozen mapping candidate","",
              "| Root | Winner | Gate | Coverage | NR exact px | NR r1 corr | NR sign | NR MAE bps |",
              "|---|---|---|---:|---:|---:|---:|---:|"]
    for root in ROOTS:
        w=winners[root]
        lines.append(
            f"| {root} | **{w['symbol']}** | **{gates[root]}** | {100*w['coverage']:.2f}% | "
            f"{100*w['nonroll_near_price_share']:.3f}% | {w['nr_r1_corr']:.6f} | {100*w['nr_r1_sign']:.3f}% | {w['nr_r1_mae_bps']:.4f} |"
        )
    lines += ["","## Governance","",
              "- V1 is not used for roll selection because one combined request caused alias attribution/deduplication.",
              "- V2 selection uses only frozen Yahoo vs Databento source agreement.",
              "- ±30 hours around Databento contract switches are excluded only for the non-roll identity diagnostic; full-window metrics remain reported.",
              "- No RESCUE/BROKEN labels, forecast correctness, Q95/Q99 outcomes or threshold tuning enter this bridge.",
              "- Raw Databento observations are processed in-memory and are not committed."]
    OUTM.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(OUTM.read_text())

if __name__=="__main__":
    main()
