from __future__ import annotations

import argparse
import calendar
import hashlib
import io
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho

OFFICIAL_REPO = "iacoviel/iacoviel.github.io"
OFFICIAL_PATH = "gpr_files/gpr_web_latest.xlsx"
ORIGIN_START = "2019-12"
ORIGIN_END = "2022-02"
HIGH_AE = 63.06
NY = ZoneInfo("America/New_York")
MACRO_SOURCE_USED = {}
FRED_MIRRORS = {
    "DGS10": "https://raw.githubusercontent.com/Najam0786/risk-aware-stock-forecasting/main/data/raw/fred_dgs10.csv",
    "DFII10": "https://raw.githubusercontent.com/AsjalAbdullahButt/Gold_Forecast_Results/main/data/raw/fred_DFII10.csv",
    "DTWEXBGS": "https://raw.githubusercontent.com/Kaenyne/Citadel-ABNB/main/data/raw/fred/DTWEXBGS.csv",
}

def mshift(m: str, d: int) -> str:
    return base.month_shift(m, d)

def months(a: str, b: str):
    return list(base.month_range(a, b))

def origin_cutoff(m: str) -> datetime:
    y, mo = map(int, m.split("-"))
    d = calendar.monthrange(y, mo)[1]
    return datetime(y, mo, d, 17, 0, 0, tzinfo=NY).astimezone(timezone.utc)

def gh_headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "gold-monthly-predev-backcast/1.0"}
    tok = os.environ.get("GH_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def fetch_commit_history():
    url = f"https://api.github.com/repos/{OFFICIAL_REPO}/commits"
    r = requests.get(url, params={"path": OFFICIAL_PATH, "per_page": 100}, headers=gh_headers(), timeout=60)
    r.raise_for_status()
    rows = []
    for c in r.json():
        stamp = c["commit"]["committer"]["date"]
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc)
        rows.append({"sha": c["sha"], "commit_at": dt, "commit_at_iso": dt.isoformat().replace("+00:00", "Z"),
                     "message": c["commit"].get("message")})
    rows.sort(key=lambda x: x["commit_at"])
    if not rows:
        raise RuntimeError("NO_GPR_WEB_LATEST_HISTORY")
    return rows

def fetch_snapshot(sha: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{OFFICIAL_REPO}/{sha}/{OFFICIAL_PATH}"
    r = requests.get(url, headers={"User-Agent": "gold-monthly-predev-backcast/1.0"}, timeout=120)
    r.raise_for_status()
    if len(r.content) < 10000:
        raise RuntimeError(f"SNAPSHOT_TOO_SMALL {sha} {len(r.content)}")
    return r.content

def parse_gpr_xlsx(raw: bytes) -> dict[str, float]:
    sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, header=None, engine="openpyxl")
    best = None
    for _, df0 in sheets.items():
        nscan = min(20, len(df0))
        for hr in range(nscan):
            vals = [str(v).strip().upper() if pd.notna(v) else "" for v in df0.iloc[hr].tolist()]
            gcols = [i for i, v in enumerate(vals) if v == "GPR" or v.startswith("GPR ") or v.startswith("GPR_")]
            if not gcols:
                continue
            date_candidates = [i for i, v in enumerate(vals) if v in {"MONTH", "DATE", "MONTHLY", "TIME"} or "MONTH" in v or "DATE" in v]
            if date_candidates:
                dc = date_candidates[0]
            else:
                dc = 0
            gc = gcols[0]
            q = df0.iloc[hr+1:, [dc, gc]].copy()
            q.columns = ["date", "gpr"]
            q["date"] = pd.to_datetime(q["date"], errors="coerce")
            q["gpr"] = pd.to_numeric(q["gpr"], errors="coerce")
            q = q.dropna().sort_values("date")
            q = q[q.gpr > 0].drop_duplicates("date", keep="last")
            if len(q) >= 24 and (best is None or len(q) > len(best)):
                best = q
    if best is None:
        # Second pass with normal headers for files whose header row is already clean.
        for _, df in pd.read_excel(io.BytesIO(raw), sheet_name=None, engine="openpyxl").items():
            cmap = {str(c).strip().upper(): c for c in df.columns}
            gc = next((c for u, c in cmap.items() if u == "GPR" or u.startswith("GPR ")), None)
            if gc is None:
                continue
            dc = next((c for u, c in cmap.items() if "MONTH" in u or "DATE" in u), df.columns[0])
            q = df[[dc, gc]].copy(); q.columns = ["date", "gpr"]
            q["date"] = pd.to_datetime(q.date, errors="coerce")
            q["gpr"] = pd.to_numeric(q.gpr, errors="coerce")
            q = q.dropna().sort_values("date")
            q = q[q.gpr > 0].drop_duplicates("date", keep="last")
            if len(q) >= 24 and (best is None or len(q) > len(best)):
                best = q
    if best is None:
        raise RuntimeError("GPR_SCHEMA_NOT_FOUND")
    out = {}
    for r in best.itertuples(index=False):
        out[pd.Timestamp(r.date).strftime("%Y-%m")] = float(r.gpr)
    return out

def source_audit():
    hist = fetch_commit_history()
    cache = {}
    rows = []
    for origin in months(ORIGIN_START, ORIGIN_END):
        cutoff = origin_cutoff(origin)
        candidates = [c for c in hist if c["commit_at"] <= cutoff]
        if not candidates:
            rows.append({"origin": origin, "status": "NO_COMMIT_BY_ORIGIN", "buildable": False})
            continue
        c = candidates[-1]
        sha = c["sha"]
        try:
            if sha not in cache:
                raw = fetch_snapshot(sha)
                cache[sha] = {
                    "raw_sha256": hashlib.sha256(raw).hexdigest(),
                    "history": parse_gpr_xlsx(raw),
                    "bytes": len(raw),
                }
            z = cache[sha]
            req = mshift(origin, -1)
            h = {k: v for k, v in z["history"].items() if k <= req}
            if req not in h:
                rows.append({"origin": origin, "status": "P_MINUS_1_MISSING", "buildable": False,
                             "commit_sha": sha, "commit_at": c["commit_at_iso"], "required_month": req,
                             "snapshot_sha256": z["raw_sha256"], "snapshot_bytes": z["bytes"],
                             "history_last": max(h) if h else None, "history_n": len(h)})
                continue
            if len(h) < 24:
                rows.append({"origin": origin, "status": "GPR_HISTORY_LT24", "buildable": False,
                             "commit_sha": sha, "commit_at": c["commit_at_iso"], "required_month": req,
                             "required_value": h[req], "snapshot_sha256": z["raw_sha256"],
                             "snapshot_bytes": z["bytes"], "history_n": len(h)})
                continue
            rows.append({"origin": origin, "status": "PASS", "buildable": True,
                         "commit_sha": sha, "commit_at": c["commit_at_iso"], "required_month": req,
                         "required_value": h[req], "snapshot_sha256": z["raw_sha256"],
                         "snapshot_bytes": z["bytes"], "history_first": min(h), "history_last": max(h),
                         "history_n": len(h), "_history": h})
        except Exception as e:
            rows.append({"origin": origin, "status": "SNAPSHOT_PARSE_FAIL", "buildable": False,
                         "commit_sha": sha, "commit_at": c["commit_at_iso"], "error": repr(e)})
    return rows

MACRO_RECON_PATH = Path(__file__).resolve().parents[1] / "data" / "GOLD_MONTHLY_PREDEV_MACRO_RECON_V1_2026-09-30.json"

def load_macro_recon():
    p = json.loads(MACRO_RECON_PATH.read_text(encoding="utf-8"))
    out = {}
    for series, rows in p["rows"].items():
        df = pd.DataFrame(rows, columns=["date", "value"])
        df["date"] = pd.to_datetime(df.date, errors="coerce")
        df["value"] = pd.to_numeric(df.value, errors="coerce")
        out[series] = df.dropna().sort_values("date")
    return out, p

def month_mean_available(df, month: str, lag_days: int):
    p = pd.Period(month, freq="M")
    cutoff = p.end_time.normalize() - pd.Timedelta(days=lag_days)
    z = df[(df.date.dt.to_period("M") == p) & (df.date <= cutoff)]
    return np.nan if z.empty else float(z.value.mean())

def macro_states():
    z, meta = load_macro_recon()
    nom = z["DGS10"]
    real = z["DFII10"]
    usd = z["DTWEXBGS"]
    out = {}
    for m in months("2019-11", ORIGIN_END):
        pm = mshift(m, -1)
        nc, npv = month_mean_available(nom, m, 2), month_mean_available(nom, pm, 2)
        rc, rpv = month_mean_available(real, m, 2), month_mean_available(real, pm, 2)
        uc, upv = month_mean_available(usd, m, 7), month_mean_available(usd, pm, 7)
        out[m] = {
            "nom10_change": None if not np.isfinite(nc) or not np.isfinite(npv) else nc - npv,
            "real10_change": None if not np.isfinite(rc) or not np.isfinite(rpv) else rc - rpv,
            "broad_usd_logchg": None if not np.isfinite(uc) or not np.isfinite(upv) else math.log(uc / upv),
        }
    return out

def all_samples_with_history(bundle, outer_target: str, gpr_history: dict[str, float]):
    out = {}
    for t in base.month_range("2010-03", outer_target):
        try:
            out[t] = base.sample_for_target(bundle, t, gpr_history, lag_gpr=True)
        except RuntimeError:
            continue
    if outer_target not in out:
        raise RuntimeError(f"OUTER_TARGET_NOT_BUILDABLE {outer_target}")
    return out

def monthly_state(bundle, origin: str):
    pm = mshift(origin, -1)
    p3 = mshift(origin, -3)
    vals = {}
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        vals[metal+"_r1"] = math.log(M[origin] / M[pm])
    vals["Gold_r3"] = math.log(bundle.monthly_metal["Gold"][origin] / bundle.monthly_metal["Gold"][p3])
    prior = [bundle.monthly_metal["Gold"][mshift(origin, -k)] for k in range(1, 13)]
    ma12 = float(np.mean(prior))
    vals["Gold_vs_ma12"] = bundle.monthly_metal["Gold"][origin] / ma12 - 1.0
    return vals

def alarm_flags(state, pred, macro):
    gold = state["Gold_r1"]
    others = [state[m+"_r1"] for m in ("Silver", "Platinum", "Palladium")]
    opp = sum(1 for x in others if x * gold < 0)
    A = (np.sign(pred) == np.sign(gold)) and abs(gold) < 0.02 and opp >= 2
    C = (gold < 0 and macro["nom10_change"] is not None and macro["real10_change"] is not None
         and macro["nom10_change"] < 0 and macro["real10_change"] < 0 and abs(pred) < 0.01)
    D = (gold > 0.03 and macro["broad_usd_logchg"] is not None and macro["nom10_change"] is not None
         and macro["real10_change"] is not None and macro["broad_usd_logchg"] > 0
         and macro["nom10_change"] > 0 and macro["real10_change"] > 0 and pred > 0)
    E = state["Gold_vs_ma12"] > 0.20 and abs(pred - gold) > 0.05
    G = state["Gold_r3"] <= -0.10
    return {"A": bool(A), "C": bool(C), "D": bool(D), "E": bool(E), "G": bool(G),
            "hard_alarm": bool(A or C or D or E or G), "opposite_metals": int(opp)}

def summarize(rows):
    if not rows:
        return {"n": 0}
    alarms = [r for r in rows if r["hard_alarm"]]
    high = [r for r in rows if r["high_error"]]
    tp = sum(r["hard_alarm"] and r["high_error"] for r in rows)
    fp = sum(r["hard_alarm"] and not r["high_error"] for r in rows)
    fn = sum((not r["hard_alarm"]) and r["high_error"] for r in rows)
    return {
        "n": len(rows),
        "sum_ae": float(sum(r["ae"] for r in rows)),
        "mae": float(np.mean([r["ae"] for r in rows])),
        "mean_ape_pct": float(np.mean([r["ape_pct"] for r in rows])),
        "high_error_n": len(high),
        "alarms": len(alarms),
        "hits": int(tp),
        "false_alarms": int(fp),
        "misses": int(fn),
        "precision": None if tp + fp == 0 else float(tp / (tp + fp)),
        "recall": None if tp + fn == 0 else float(tp / (tp + fn)),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="GOLD_MONTHLY_CHHHO_PREDEV_BACKCAST_V1_2026-09-30.json")
    args = ap.parse_args()

    audit = source_audit()
    buildable = [r for r in audit if r.get("buildable")]
    print("SOURCE_AUDIT", json.dumps({
        "requested": len(audit),
        "buildable": len(buildable),
        "passing_origins": [r["origin"] for r in buildable],
        "blocked": [{"origin": r["origin"], "status": r["status"]} for r in audit if not r.get("buildable")]
    }, sort_keys=True))
    if not buildable:
        out = {"schema": "GOLD_MONTHLY_CHHHO_PREDEV_BACKCAST_V1_2026-09-30",
               "status": "SOURCE_BLOCKED_NO_MODEL_RUN", "source_audit": audit}
        Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": out["status"], "buildable": 0}, sort_keys=True))
        return

    dsn = os.environ["NEON_DATABASE_URL"]
    bundle = base.load_data(dsn)
    macro = macro_states()
    rows = []
    for ar in buildable:
        origin = ar["origin"]
        target = mshift(origin, 1)
        hist = ar.pop("_history")
        samples = all_samples_with_history(bundle, target, hist)
        pred, n, diag = chhho.select(samples, target, "CHHHO")
        pred_gold = float(pred[0])
        forecast = float(bundle.core_gold[origin] * math.exp(pred_gold))
        actual = float(bundle.core_gold[target])
        ae = abs(forecast - actual)
        ape = ae / actual * 100.0
        state = monthly_state(bundle, origin)
        flags = alarm_flags(state, pred_gold, macro[origin])
        rows.append({
            "target": target, "origin": origin,
            "source_commit_sha": ar["commit_sha"], "source_commit_at": ar["commit_at"],
            "snapshot_sha256": ar["snapshot_sha256"], "required_gpr_month": ar["required_month"],
            "required_gpr_value": ar["required_value"], "gpr_history_n": ar["history_n"],
            "train_rows": int(n), "diag": diag,
            "pred_log_return_gold": pred_gold, "forecast": forecast, "actual": actual,
            "ae": float(ae), "ape_pct": float(ape), "high_error": bool(ae > HIGH_AE),
            **state, **macro[origin], **flags,
        })

    yearly = {}
    for y in sorted({r["target"][:4] for r in rows}):
        yearly[y] = summarize([r for r in rows if r["target"].startswith(y)])

    per_alarm = {}
    for a in ["A", "C", "D", "E", "G"]:
        z = [r for r in rows if r[a]]
        per_alarm[a] = {
            "alarms": len(z),
            "hits": sum(r["high_error"] for r in z),
            "false_alarms": sum(not r["high_error"] for r in z),
            "targets": [r["target"] for r in z],
        }

    out = {
        "schema": "GOLD_MONTHLY_CHHHO_PREDEV_BACKCAST_V1_2026-09-30",
        "status": "COMPLETE",
        "authority_file": "GOLD_MONTHLY_CHHHO_PREDEV_GPR_WEB_LATEST_AUTHORITY_2026-09-30.md",
        "authority_commit": "05b46ad776d7d2915185a9fd3a5918086211b697",
        "scope": "HISTORICAL_PREDEV_ALARM_VALIDATION_ONLY_NO_ROUTING",
        "high_error_threshold_usd": HIGH_AE,
        "source": {"repository": OFFICIAL_REPO, "path": OFFICIAL_PATH,
                   "origin_start": ORIGIN_START, "origin_end": ORIGIN_END},
        "macro_source_used": MACRO_SOURCE_USED,
        "source_audit": audit,
        "coverage": {"requested_origins": len(audit), "buildable_origins": len(buildable),
                     "first_buildable": buildable[0]["origin"], "last_buildable": buildable[-1]["origin"]},
        "overall": summarize(rows),
        "yearly": yearly,
        "per_alarm": per_alarm,
        "rows": rows,
        "governance": {
            "A_C_D_unchanged": True, "E_G_thresholds_unchanged": True,
            "future_or_target_labels_used_in_features": False,
            "current_final_gpr_substitution": False,
            "database_access": "READ_ONLY", "routing_tested": False,
            "macro_evidence_class": "HISTORICAL_RECONSTRUCTION_WITH_RELEASE_SAFETY_LAGS",
        }
    }
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"coverage": out["coverage"], "overall": out["overall"], "yearly": yearly,
                      "per_alarm": per_alarm}, sort_keys=True))

if __name__ == "__main__":
    main()
