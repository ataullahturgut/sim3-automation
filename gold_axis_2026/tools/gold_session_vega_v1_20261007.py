from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
RIFT_PATH = AX / "tools" / "gold_session_rift_v1_20261007.py"
GVZ_PATH = AX / "GOLD_GVZCLS_RAW_2021_2025.csv"
OUT = AX / "SESSION_VEGA_V1_OUT"
OUT.mkdir(exist_ok=True)

THRESH = 0.70
MIN_TRAIN = 80
SEED = 20261007
EPS = 1e-8

FEATURES = [
    "gvz_z252",
    "gvz_r1",
    "gvz_r3",
    "gvz_r5",
    "gvz_vs_med20",
    "iv_rv24_gap",
    "iv_rv48_gap",
    "trend_strength",
    "gvz_shock_x_trend",
]


def loadmod(name: str, path: Path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    assert s.loader is not None
    s.loader.exec_module(m)
    return m


rift = loadmod("session_rift", RIFT_PATH)


def load_gvz() -> pd.DataFrame:
    q = pd.read_csv(GVZ_PATH)
    q["date"] = pd.to_datetime(q.date, errors="raise")
    q["value"] = pd.to_numeric(q.value, errors="raise")
    q = q.dropna().sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    if q.date.min() > pd.Timestamp("2021-01-10") or q.date.max() < pd.Timestamp("2024-12-31"):
        raise RuntimeError(f"GVZ_COVERAGE_FAIL min={q.date.min()} max={q.date.max()}")
    return q


def gvz_features(gvz: pd.DataFrame, origin_ny_date) -> dict | None:
    cutoff = pd.Timestamp(origin_ny_date) - pd.Timedelta(days=1)
    q = gvz[gvz.date <= cutoff]
    if len(q) < 253:
        return None

    vals = q.value.to_numpy(float)
    cur = float(vals[-1])
    hist252 = vals[-253:-1]
    med20 = float(np.median(vals[-21:-1]))
    mu = float(np.mean(hist252))
    sd = float(np.std(hist252, ddof=0))

    return {
        "gvz_date_used": q.iloc[-1].date,
        "gvz_level": cur,
        "gvz_z252": (cur - mu) / (sd if sd > EPS else 1.0),
        "gvz_r1": float(math.log(cur / vals[-2])),
        "gvz_r3": float(math.log(cur / vals[-4])),
        "gvz_r5": float(math.log(cur / vals[-6])),
        "gvz_vs_med20": float(math.log(cur / med20)),
    }


def build_panel() -> pd.DataFrame:
    p = rift.load_targets().reset_index(drop=True)
    p["row_id"] = np.arange(len(p))
    p = rift.ma15.attach(p, rift.load_raw15(), "g")

    req = [
        "g_ret_12h", "g_rv_12", "g_rv_24", "g_rv_48",
        "g_anchor_available", "g_max_reference_stale_min",
    ]
    p = p.dropna(subset=req + ["direction"]).copy()

    if not (p.g_anchor_available < p.start_utc).all():
        raise RuntimeError("VEGA_XAU_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():
        raise RuntimeError("VEGA_REFERENCE_STALE")

    gvz = load_gvz()
    rec = []
    for r in p.itertuples(index=False):
        origin_ny_date = pd.Timestamp(r.start_utc).tz_convert("America/New_York").date()
        gf = gvz_features(gvz, origin_ny_date)
        if gf is None:
            continue

        implied_daily = float(gf["gvz_level"]) / 100.0 / math.sqrt(252.0)
        rv24 = float(r.g_rv_24)
        rv48_daily = float(r.g_rv_48) / math.sqrt(2.0)
        trend_strength = abs(float(r.g_ret_12h)) / (float(r.g_rv_12) + EPS)

        d = r._asdict()
        d.update({
            **gf,
            "origin_ny_date": str(origin_ny_date),
            "trend_strength": trend_strength,
            "iv_rv24_gap": float(math.log((implied_daily + EPS) / (rv24 + EPS))),
            "iv_rv48_gap": float(math.log((implied_daily + EPS) / (rv48_daily + EPS))),
            "gvz_shock_x_trend": float(gf["gvz_r3"]) * trend_strength,
            "momentum_up": int(float(r.g_ret_12h) >= 0),
        })
        d["reversal_target"] = int(int(r.y_up) != d["momentum_up"])
        rec.append(d)

    q = pd.DataFrame(rec)
    if q.empty:
        raise RuntimeError("VEGA_EMPTY_PANEL")

    q["start_utc"] = pd.to_datetime(q.start_utc, utc=True)
    q["end_utc"] = pd.to_datetime(q.end_utc, utc=True)
    q["year"] = q.start_utc.dt.year
    q["month_key"] = q.start_utc.dt.to_period("M").astype(str)

    # Hard D-1 calendar guard relative to actual NY origin date.
    q["gvz_date_used"] = pd.to_datetime(q.gvz_date_used)
    origin_dates = pd.to_datetime(q.origin_ny_date)
    if not (q.gvz_date_used <= origin_dates - pd.Timedelta(days=1)).all():
        raise RuntimeError("VEGA_GVZ_DMINUS1_FAIL")

    return q.sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)


def make_model():
    return LogisticRegression(
        C=1.0,
        solver="lbfgs",
        max_iter=5000,
        class_weight="balanced",
        random_state=SEED,
    )


def replay_vega(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (part, win), g0 in panel.groupby(["partition", "window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True)
        teall = g[g.year.isin([2023, 2024])].copy()

        for mo in sorted(teall.month_key.unique()):
            te = teall[teall.month_key == mo].copy()
            cutoff = te.start_utc.min()
            tr = g[(g.end_utc <= cutoff) & (g.start_utc < cutoff)].copy()

            if len(tr) < MIN_TRAIN or tr.reversal_target.nunique() < 2:
                continue

            X = tr[FEATURES].astype(float).to_numpy()
            Xt = te[FEATURES].astype(float).to_numpy()
            sc = StandardScaler().fit(X)
            m = make_model().fit(sc.transform(X), tr.reversal_target.astype(int).to_numpy())
            pr = m.predict_proba(sc.transform(Xt))[:, 1]

            for r, p_rev in zip(te.itertuples(index=False), pr):
                rows.append({
                    "partition": part,
                    "window": win,
                    "label_date": r.label_date,
                    "start_utc": r.start_utc,
                    "end_utc": r.end_utc,
                    "year": int(r.year),
                    "y_up": int(r.y_up),
                    "momentum_up": int(r.momentum_up),
                    "p_reversal": float(p_rev),
                    "reversal_target": int(r.reversal_target),
                    "gvz_date_used": pd.Timestamp(r.gvz_date_used).date().isoformat(),
                    "train_n": int(len(tr)),
                })

    return pd.DataFrame(rows).sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)


def main():
    panel = build_panel()
    pred = replay_vega(panel)
    pred.to_csv(OUT / "vega_predictions.csv", index=False)

    all_metrics = []
    changed = []
    for name, base in rift.load_baselines().items():
        z, rows = rift.correct(base, pred, name)
        all_metrics.extend(rows)
        if not z.empty:
            q = z[z.override].copy()
            if not q.empty:
                q["baseline_name"] = name
                changed.append(q)

    mdf = pd.DataFrame(all_metrics)
    gate = rift.pass_table(mdf)

    mdf.to_csv(OUT / "metrics.csv", index=False)
    gate.to_csv(OUT / "transport_eligibility.csv", index=False)
    if changed:
        pd.concat(changed, ignore_index=True).to_csv(OUT / "changed_calls.csv", index=False)

    summary = {
        "status": "SESSION_VEGA_V1_DEVELOPMENT_COMPLETE",
        "scope": "2022 warm-up; 2023-2024 development only; 2025 not used for VEGA fitting or gate selection",
        "threshold": THRESH,
        "gvz_source": GVZ_PATH.name,
        "gvz_rule": "latest observation dated <= NY origin date D-1 calendar day",
        "features": FEATURES,
        "vega_rows": int(len(pred)),
        "transport_eligible": gate[gate.transport_eligible].to_dict("records"),
        "metrics": mdf.to_dict("records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# SESSION VEGA V1 — DEVELOPMENT RESULT",
        "",
        "**Status:** SESSION_VEGA_V1_DEVELOPMENT_COMPLETE",
        "",
        "- 2022 warm-up only.",
        "- 2023-2024 development only.",
        "- GVZ use is D-1 calendar day or earlier relative to the actual NY session-origin date.",
        "- Fixed reversal threshold: 0.70.",
        "- No 2025 outcome used for VEGA fit or gate selection.",
        "",
        "## Transport-eligible window/baseline pairs",
        "",
    ]
    if gate.transport_eligible.any():
        for r in gate[gate.transport_eligible].itertuples(index=False):
            lines.append(f"- {r.partition} / {r.window} / {r.baseline}")
    else:
        lines.append("- none")

    lines += [
        "",
        "## Combined 2023-2024 metrics",
        "",
        "| Baseline | Partition | Window | N | Base BA | VEGA BA | Base Brier | VEGA Brier | Overrides | Rescue | Break | Net |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in mdf[mdf.period == "2023-2024"].itertuples(index=False):
        lines.append(
            f"| {r.baseline} | {r.partition} | {r.window} | {r.n} | "
            f"{100*r.base_balanced_accuracy:.2f}% | {100*r.rift_balanced_accuracy:.2f}% | "
            f"{r.base_brier:.4f} | {r.rift_brier:.4f} | {r.override_n} | "
            f"{r.rescued} | {r.broken} | {r.net_rescue} |"
        )

    (OUT / "result.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({
        "status": summary["status"],
        "vega_rows": len(pred),
        "eligible": summary["transport_eligible"],
    }, indent=2))


if __name__ == "__main__":
    main()
