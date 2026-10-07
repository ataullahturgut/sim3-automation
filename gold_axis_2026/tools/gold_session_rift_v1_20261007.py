from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, recall_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"

MA15_PATH = AX / "tools" / "gold_session_iris15_crossmetal_v2_maintaware_20261006.py"
WARM = AX / "GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
WGC = AX / "GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB = AX / "GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
RAW22 = AX / "GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
RAW35 = AX / "GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"

A0 = AX / "GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv"
PATH = AX / "GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv"
S14 = AX / "GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_PREDICTIONS_2026-10-07.csv"

OUT = AX / "SESSION_RIFT_V1_OUT"
OUT.mkdir(exist_ok=True)

THRESH = 0.70
MIN_TRAIN = 80
SEED = 20261007
EPS = 1e-8

FEATURES = [
    "trend_strength",
    "opposite_semivar_share",
    "deceleration_6h",
    "path_consistency",
    "trend_close_location",
    "opposite_extreme_recency",
    "jump_concentration_24",
    "trend_to_range",
    "adverse_excursion",
]

KEY = ["partition", "window", "label_date", "start_utc", "y_up"]


def loadmod(name: str, path: Path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    assert s.loader is not None
    s.loader.exec_module(m)
    return m


ma15 = loadmod("ma15", MA15_PATH)


def asbool(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().eq("true")


def load_targets() -> pd.DataFrame:
    w = pd.read_csv(WARM)
    w = w[asbool(w.final_trainable)].copy()

    z = []
    for p in [WGC, SOB]:
        q = pd.read_csv(p)
        q = q[asbool(q.final_trainable)].copy()
        q["start_utc"] = pd.to_datetime(q.start_utc, utc=True)
        q = q[q.start_utc.dt.year.isin([2023, 2024])].copy()
        z.append(q)

    q = pd.concat([w] + z, ignore_index=True, sort=False)
    q["start_utc"] = pd.to_datetime(q.start_utc, utc=True, errors="raise")
    q["end_utc"] = pd.to_datetime(q.end_utc, utc=True, errors="raise")
    q["label_date"] = pd.to_datetime(q.label_date).dt.strftime("%Y-%m-%d")
    q["year"] = q.start_utc.dt.year
    q["y_up"] = (q.direction == "UP").astype(int)

    if q.duplicated(["partition", "window", "label_date"]).any():
        raise RuntimeError("TARGET_DUPLICATE")

    return q.sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)


def load_raw15() -> pd.DataFrame:
    a = pd.read_csv(RAW22, usecols=["dt_utc", "close"])
    b = pd.read_csv(RAW35, usecols=["dt_utc", "close"])

    for q in [a, b]:
        q["dt_utc"] = pd.to_datetime(q.dt_utc, utc=True, errors="raise")
        q["close"] = pd.to_numeric(q.close, errors="raise")

    q = pd.concat([a, b], ignore_index=True).sort_values("dt_utc")
    q = q[q.dt_utc < pd.Timestamp("2025-01-01", tz="UTC")].copy()

    d = q[q.duplicated("dt_utc", keep=False)]
    if not d.empty and d.groupby("dt_utc").close.nunique().gt(1).any():
        raise RuntimeError("RAW_OVERLAP_CONFLICT")

    q = q.drop_duplicates("dt_utc", keep="last")
    q = q.rename(columns={"dt_utc": "ts", "close": "value"})
    q["available_at_utc"] = q.ts + pd.Timedelta(minutes=15)
    return q[["ts", "available_at_utc", "value"]].reset_index(drop=True)


def build_panel() -> pd.DataFrame:
    p = load_targets().reset_index(drop=True)
    p["row_id"] = np.arange(len(p))
    p = ma15.attach(p, load_raw15(), "g")

    req = [
        "g_ret_6h", "g_ret_12h", "g_rv_12",
        "g_up_semivol_24", "g_down_semivol_24",
        "g_upfrac_24", "g_close_location_24",
        "g_age_max_neg_24", "g_age_max_pos_24",
        "g_jump_concentration_24", "g_range_24",
        "g_max_drawdown_24", "g_recovery_24",
        "g_anchor_available", "g_max_reference_stale_min",
    ]
    p = p.dropna(subset=req + ["direction"]).copy()

    if not (p.g_anchor_available < p.start_utc).all():
        raise RuntimeError("RIFT_XAU_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():
        raise RuntimeError("RIFT_REFERENCE_STALE")

    sign = np.where(p.g_ret_12h.to_numpy(float) >= 0, 1.0, -1.0)
    up2 = p.g_up_semivol_24.to_numpy(float) ** 2
    dn2 = p.g_down_semivol_24.to_numpy(float) ** 2
    total = up2 + dn2 + EPS

    p["trend_strength"] = np.abs(p.g_ret_12h) / (p.g_rv_12 + EPS)
    p["opposite_semivar_share"] = np.where(sign > 0, dn2 / total, up2 / total)
    p["deceleration_6h"] = -sign * (2.0 * p.g_ret_6h - p.g_ret_12h) / (p.g_rv_12 + EPS)
    p["path_consistency"] = sign * (2.0 * p.g_upfrac_24 - 1.0)
    p["trend_close_location"] = np.where(
        sign > 0, p.g_close_location_24, 1.0 - p.g_close_location_24
    )
    p["opposite_extreme_recency"] = np.where(
        sign > 0,
        1.0 / (1.0 + p.g_age_max_neg_24),
        1.0 / (1.0 + p.g_age_max_pos_24),
    )
    p["jump_concentration_24"] = p.g_jump_concentration_24
    p["trend_to_range"] = np.abs(p.g_ret_12h) / (p.g_range_24 + EPS)
    p["adverse_excursion"] = np.where(
        sign > 0,
        -p.g_max_drawdown_24 / (p.g_range_24 + EPS),
        p.g_recovery_24 / (p.g_range_24 + EPS),
    )

    p["momentum_up"] = (p.g_ret_12h >= 0).astype(int)
    p["reversal_target"] = (p.y_up.astype(int) != p.momentum_up.astype(int)).astype(int)
    p["month_key"] = p.start_utc.dt.to_period("M").astype(str)

    return p.sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)


def make_model():
    return LogisticRegression(
        C=1.0,
        solver="lbfgs",
        max_iter=5000,
        class_weight="balanced",
        random_state=SEED,
    )


def replay_rift(panel: pd.DataFrame) -> pd.DataFrame:
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
                    "train_n": int(len(tr)),
                })

    return pd.DataFrame(rows).sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)


def load_baselines() -> dict[str, pd.DataFrame]:
    out = {}

    a = pd.read_csv(A0)
    a["start_utc"] = pd.to_datetime(a.start_utc, utc=True)
    a["label_date"] = pd.to_datetime(a.label_date).dt.strftime("%Y-%m-%d")
    out["A0_CORE3"] = a[KEY + ["p_up"]].copy()

    p = pd.read_csv(PATH)
    p["start_utc"] = pd.to_datetime(p.start_utc, utc=True)
    p["label_date"] = pd.to_datetime(p.label_date).dt.strftime("%Y-%m-%d")
    out["PATH_GLOBAL_1H"] = p[KEY + ["p_up"]].copy()

    s = pd.read_csv(S14)
    s["start_utc"] = pd.to_datetime(s.start_utc, utc=True)
    s["label_date"] = pd.to_datetime(s.label_date).dt.strftime("%Y-%m-%d")

    a1 = s[s.model == "A1_DIRECT_MATCHED"][KEY + ["p_up"]].copy()
    out["A1_ARCR"] = a1

    si = s[s.model == "S14_A1_PLUS_1H_FULL"][KEY + ["p_up"]].copy()
    out["STRUCTURAL_IRIS_A1_PLUS_1H"] = si

    return out


def metric(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p - y) ** 2)),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
    }


def correct(base: pd.DataFrame, rift: pd.DataFrame, name: str):
    z = base.merge(
        rift[KEY + ["momentum_up", "p_reversal"]],
        on=KEY,
        how="inner",
        validate="one_to_one",
    )
    if z.empty:
        return pd.DataFrame(), []

    bpred = (z.p_up >= 0.5).astype(int)
    follows = bpred.eq(z.momentum_up.astype(int))
    override = follows & z.p_reversal.ge(THRESH)

    z["override"] = override
    z["p_corrected"] = z.p_up.astype(float)

    upmom = z.momentum_up.astype(int).eq(1)
    z.loc[override & upmom, "p_corrected"] = 1.0 - z.loc[override & upmom, "p_reversal"]
    z.loc[override & (~upmom), "p_corrected"] = z.loc[override & (~upmom), "p_reversal"]
    z["baseline"] = name

    rows = []
    for (part, win), g in z.groupby(["partition", "window"], sort=True):
        for period, q in [
            ("2023", g[g.start_utc.dt.year == 2023]),
            ("2024", g[g.start_utc.dt.year == 2024]),
            ("2023-2024", g),
        ]:
            if q.empty:
                continue

            mb = metric(q.y_up, q.p_up)
            mr = metric(q.y_up, q.p_corrected)

            bp = (q.p_up >= 0.5).astype(int)
            rp = (q.p_corrected >= 0.5).astype(int)
            y = q.y_up.astype(int)
            changed = bp.ne(rp)
            rescued = int((changed & bp.ne(y) & rp.eq(y)).sum())
            broken = int((changed & bp.eq(y) & rp.ne(y)).sum())

            rows.append({
                "baseline": name,
                "partition": part,
                "window": win,
                "period": period,
                "n": int(len(q)),
                "override_n": int(q.override.sum()),
                "changed_n": int(changed.sum()),
                "rescued": rescued,
                "broken": broken,
                "net_rescue": rescued - broken,
                **{f"base_{k}": v for k, v in mb.items()},
                **{f"rift_{k}": v for k, v in mr.items()},
            })
    return z, rows


def pass_table(mdf: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (base, part, win), g in mdf.groupby(["baseline", "partition", "window"], sort=True):
        by = {r.period: r for r in g.itertuples(index=False)}
        req = all(x in by for x in ["2023", "2024", "2023-2024"])
        if not req:
            passed = False
            reason = "MISSING_YEAR"
        else:
            r23 = by["2023"]
            r24 = by["2024"]
            ra = by["2023-2024"]

            checks = [
                r23.rift_accuracy + 0.01 + 1e-12 >= r23.base_accuracy,
                r24.rift_accuracy + 0.01 + 1e-12 >= r24.base_accuracy,
                r23.rift_brier <= r23.base_brier + 0.003 + 1e-12,
                r24.rift_brier <= r24.base_brier + 0.003 + 1e-12,
                ra.rift_balanced_accuracy + 1e-12 >= ra.base_balanced_accuracy,
                int(ra.net_rescue) > 0,
                min(ra.rift_up_recall, ra.rift_down_recall) >= 0.30,
            ]
            passed = bool(all(checks))
            reason = "PASS" if passed else "GATE_FAIL"

        out.append({
            "baseline": base,
            "partition": part,
            "window": win,
            "transport_eligible": passed,
            "reason": reason,
        })
    return pd.DataFrame(out)


def main():
    panel = build_panel()
    rift = replay_rift(panel)
    rift.to_csv(OUT / "rift_predictions.csv", index=False)

    all_metrics = []
    changed = []
    for name, base in load_baselines().items():
        z, rows = correct(base, rift, name)
        all_metrics.extend(rows)
        if not z.empty:
            q = z[z.override].copy()
            if not q.empty:
                q["baseline_name"] = name
                changed.append(q)

    mdf = pd.DataFrame(all_metrics)
    gate = pass_table(mdf)

    mdf.to_csv(OUT / "metrics.csv", index=False)
    gate.to_csv(OUT / "transport_eligibility.csv", index=False)
    if changed:
        pd.concat(changed, ignore_index=True).to_csv(OUT / "changed_calls.csv", index=False)

    summary = {
        "status": "SESSION_RIFT_V1_DEVELOPMENT_COMPLETE",
        "scope": "2022 warm-up; 2023-2024 development only; 2025 not used for RIFT fitting or gate selection",
        "threshold": THRESH,
        "features": FEATURES,
        "feature_omission": "Historical H3 session_against_trend omitted; no session-clock-safe replacement searched.",
        "rift_rows": int(len(rift)),
        "transport_eligible": gate[gate.transport_eligible].to_dict("records"),
        "metrics": mdf.to_dict("records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# SESSION RIFT V1 — DEVELOPMENT RESULT",
        "",
        "**Status:** SESSION_RIFT_V1_DEVELOPMENT_COMPLETE",
        "",
        "- 2022 warm-up only.",
        "- 2023-2024 development only.",
        "- Fixed reversal threshold: 0.70.",
        "- No 2025 outcome used for RIFT fit or gate selection.",
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
        "| Baseline | Partition | Window | N | Base BA | RIFT BA | Base Brier | RIFT Brier | Overrides | Rescue | Break | Net |",
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
        "rift_rows": len(rift),
        "eligible": summary["transport_eligible"],
    }, indent=2))


if __name__ == "__main__":
    main()
