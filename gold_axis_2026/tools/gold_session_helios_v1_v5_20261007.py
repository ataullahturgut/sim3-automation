from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "SESSION_HELIOS_V1_V5_OUT"
OUT.mkdir(exist_ok=True)

OPALP = AX / "tools" / "gold_session_opal_v1_20261007.py"
TURNP = AX / "tools" / "gold_session_turn_v1_20261007.py"
RIFT25P = AX / "tools" / "gold_session_rift_frozen_2025_transport_20261007.py"
VEGA25P = AX / "tools" / "gold_session_vega_frozen_2025_transport_20261007.py"

def loadmod(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    assert s.loader is not None
    s.loader.exec_module(m)
    return m

opal = loadmod("session_opal", OPALP)
turn = loadmod("session_turn", TURNP)
rift25 = loadmod("session_rift25", RIFT25P)
vega25 = loadmod("session_vega25", VEGA25P)

KEY = ["partition", "window", "start_utc", "end_utc"]

V1_WINDOW = 8
V1_ENTER_WINS = 5
V1_EXIT_WINS = 3

GT_WINDOW = 8
GT_BROKEN_COST = 1.0
GT_THRESHOLD = 0.50
POLICIES = ["KEEP", "HELIOS_CONSENSUS", "COT_FRESH", "FRESH_OR_CONSENSUS", "OPAL_ALL"]

RGE_WINDOW = 10
RGE_ENTER = 2
RGE_EXIT = -2
RGE_THRESHOLD = 0.50

DCE_POSTERIOR = 0.50
DCE_GT = 0.50

def metric(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "up_actual": int((y == 1).sum()),
        "up_correct": int(((y == 1) & (pred == 1)).sum()),
        "down_actual": int((y == 0).sum()),
        "down_correct": int(((y == 0) & (pred == 0)).sum()),
    }

def replay_reversal(panel, features, model_fn, min_train, years, extra_cols=()):
    rows = []
    for (part, win), g0 in panel.groupby(["partition", "window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True)
        teall = g[g.year.isin(list(years))].copy()
        for mo in sorted(teall.month_key.unique()):
            te = teall[teall.month_key.eq(mo)].copy()
            if te.empty:
                continue
            cutoff = te.start_utc.min()
            tr = g[(g.end_utc <= cutoff) & (g.start_utc < cutoff)].copy()
            if len(tr) < int(min_train) or tr.reversal_target.nunique() < 2:
                continue
            X = tr[list(features)].astype(float).to_numpy()
            Xt = te[list(features)].astype(float).to_numpy()
            sc = StandardScaler().fit(X)
            m = model_fn().fit(sc.transform(X), tr.reversal_target.astype(int).to_numpy())
            pr = m.predict_proba(sc.transform(Xt))[:, 1]
            for r, pv in zip(te.itertuples(index=False), pr):
                rec = {
                    "partition": part, "window": win,
                    "start_utc": r.start_utc, "end_utc": r.end_utc,
                    "year": int(r.year), "y_up": int(r.y_up),
                    "momentum_up": int(r.momentum_up),
                    "p_reversal": float(pv),
                    "train_n": int(len(tr)),
                }
                for c in extra_cols:
                    rec[c] = getattr(r, c)
                rows.append(rec)
    if not rows:
        return pd.DataFrame(columns=KEY + ["year","y_up","momentum_up","p_reversal","train_n"])
    return pd.DataFrame(rows).sort_values(KEY).reset_index(drop=True)

def build_common_ledger():
    a = opal.fresh_aurora_ledger().copy()
    a["start_utc"] = pd.to_datetime(a.start_utc, utc=True)
    a["end_utc"] = pd.to_datetime(a.end_utc, utc=True)
    a["year"] = a.start_utc.dt.year
    keepa = KEY + [
        "label_date","year","y_up","p_aurora","active_expert",
        "prob_path_superior","q_path"
    ]
    a = a[keepa].copy()

    opanel = opal.build_panel()
    orows = []
    for (_, _), g in opanel.groupby(["partition","window"], sort=True):
        z = opal.run_window(g, [2023, 2024, 2025])
        if not z.empty:
            orows.append(z)
    o = pd.concat(orows, ignore_index=True)
    o["start_utc"] = pd.to_datetime(o.start_utc, utc=True)
    o["end_utc"] = pd.to_datetime(o.end_utc, utc=True)
    o = o[KEY + ["p_reversal","override","p_opal","cot_report_date","cot_available_at_utc"]].copy()
    o = o.rename(columns={
        "p_reversal":"p_opal_reversal",
        "override":"opal_override",
    })

    rp = rift25.build_panel()
    r = replay_reversal(
        rp, rift25.FULL, rift25.model, rift25.MIN_TRAIN,
        [2023, 2024, 2025]
    )
    r = r[KEY + ["momentum_up","p_reversal"]].rename(columns={
        "momentum_up":"rift_momentum_up",
        "p_reversal":"p_rift_reversal",
    })

    vp = vega25.build_panel()
    v = replay_reversal(
        vp, vega25.FEATURES, vega25.model, vega25.MIN_TRAIN,
        [2023, 2024, 2025], extra_cols=("gvz_date_used",)
    )
    v = v[KEY + ["momentum_up","p_reversal"]].rename(columns={
        "momentum_up":"vega_momentum_up",
        "p_reversal":"p_vega_reversal",
    })

    t = turn.build_panel().copy()
    t["start_utc"] = pd.to_datetime(t.start_utc, utc=True)
    t["end_utc"] = pd.to_datetime(t.end_utc, utc=True)
    t = t[KEY + ["override"]].rename(columns={"override":"turn_override"})

    g = a.merge(o, on=KEY, how="inner", validate="one_to_one")
    g = g.merge(r, on=KEY, how="inner", validate="one_to_one")
    g = g.merge(v, on=KEY, how="inner", validate="one_to_one")
    g = g.merge(t, on=KEY, how="inner", validate="one_to_one")
    if g.empty:
        raise RuntimeError("HELIOS_EMPTY_COMMON_LEDGER")

    g["aurora_pred"] = (g.p_aurora.astype(float) >= .5).astype(int)
    g["rift_override"] = (
        g.aurora_pred.eq(g.rift_momentum_up.astype(int))
        & g.p_rift_reversal.astype(float).ge(float(rift25.THRESH))
    )
    g["vega_override"] = (
        g.aurora_pred.eq(g.vega_momentum_up.astype(int))
        & g.p_vega_reversal.astype(float).ge(float(vega25.THRESH))
    )
    g["turn_override"] = g.turn_override.astype(bool)
    g["opal_override"] = g.opal_override.astype(bool)

    g["corroborator_n"] = (
        g.rift_override.astype(int)
        + g.turn_override.astype(int)
        + g.vega_override.astype(int)
    )
    g["candidate_reversal"] = g.opal_override & g.corroborator_n.ge(1)
    g["candidate_success"] = np.where(
        g.candidate_reversal,
        g.aurora_pred.ne(g.y_up.astype(int)).astype(float),
        np.nan,
    )
    g["opal_rescue_success"] = np.where(
        g.opal_override,
        g.aurora_pred.ne(g.y_up.astype(int)).astype(float),
        np.nan,
    )

    # COT freshness is independent by partition/window.
    fresh = pd.Series(False, index=g.index)
    for (_, _), idx in g.groupby(["partition","window"], sort=False).groups.items():
        seen = {}
        for i in sorted(idx, key=lambda j: g.loc[j, "start_utc"]):
            if bool(g.loc[i, "opal_override"]):
                k = str(g.loc[i, "cot_report_date"])
                seen[k] = seen.get(k, 0) + 1
                fresh.loc[i] = seen[k] == 1
    g["cot_fresh"] = fresh.astype(bool)

    g = g.sort_values(["partition","window","start_utc"]).reset_index(drop=True)
    return g

def simulate_v1_v2(g0):
    rows = []
    for (part, win), g in g0.groupby(["partition","window"], sort=True):
        g = g.sort_values("start_utc").reset_index(drop=True)
        hist, pending = [], []
        active = False
        for r in g.itertuples(index=False):
            keep = []
            for item in pending:
                if pd.Timestamp(item["end_utc"]) <= pd.Timestamp(r.start_utc):
                    hist.append(int(item["success"]))
                else:
                    keep.append(item)
            pending = keep
            recent = hist[-V1_WINDOW:]
            wins = int(sum(recent)) if len(recent) >= V1_WINDOW else 0
            old = active
            if len(recent) >= V1_WINDOW:
                if (not active) and wins >= V1_ENTER_WINS:
                    active = True
                elif active and wins <= V1_EXIT_WINS:
                    active = False
            candidate = bool(r.candidate_reversal)
            hard_route = bool(active and candidate)
            q = float((wins + 1) / (V1_WINDOW + 2)) if len(recent) >= V1_WINDOW else 0.5
            pa = float(r.p_aurora)
            p_hard = float(1.0 - pa) if hard_route else pa
            p_soft = float((1.0 - q) * pa + q * (1.0 - pa)) if hard_route else pa
            if hard_route:
                p_v2 = float(1.0 - q) if pa >= .5 else float(q)
            else:
                p_v2 = pa

            rec = r._asdict()
            rec.update({
                "gate_active": bool(active),
                "v1_state_changed": bool(active != old),
                "competence_matured_n": int(len(hist)),
                "recent_candidate_n": int(len(recent)),
                "recent_wins": int(wins),
                "recent_losses": int(len(recent) - wins),
                "competence_q": q,
                "hard_route": hard_route,
                "p_helios_v1_hard": p_hard,
                "p_helios_v1_soft": p_soft,
                "p_helios_v2": p_v2,
            })
            rows.append(rec)
            if candidate:
                pending.append({
                    "end_utc": r.end_utc,
                    "success": int(r.candidate_success),
                })
    return pd.DataFrame(rows)

def policy_votes(row):
    consensus = bool(row.candidate_reversal)
    fresh = bool(row.cot_fresh)
    return {
        "KEEP": 0,
        "HELIOS_CONSENSUS": int(consensus),
        "COT_FRESH": int(fresh),
        "FRESH_OR_CONSENSUS": int(fresh or consensus),
        "OPAL_ALL": 1,
    }

def add_v3(g0):
    rows = []
    eta = math.sqrt(8.0 * math.log(len(POLICIES)) / float(GT_WINDOW))
    for (part, win), g in g0.groupby(["partition","window"], sort=True):
        g = g.sort_values("start_utc").reset_index(drop=True)
        hist, pending = [], []
        for r in g.itertuples(index=False):
            keep = []
            for item in pending:
                if pd.Timestamp(item["end_utc"]) <= pd.Timestamp(r.start_utc):
                    hist.append(item)
                else:
                    keep.append(item)
            pending = keep
            recent = hist[-GT_WINDOW:]
            votes = policy_votes(r)
            util = {}
            logw = {}
            for name in POLICIES:
                u = 0.0
                for e in recent:
                    if e["votes"][name]:
                        u += 1.0 if e["success"] else -GT_BROKEN_COST
                util[name] = u
                logw[name] = eta * u
            mx = max(logw.values())
            w = {k: math.exp(v - mx) for k, v in logw.items()}
            den = sum(w.values())
            norm = {k: w[k] / den for k in POLICIES}
            share = float(sum(norm[k] * votes[k] for k in POLICIES))
            route = bool(r.gate_active and r.opal_override and share > GT_THRESHOLD)
            pa = float(r.p_aurora)
            rec = r._asdict()
            rec.update({
                "gt_matured_opal_n": int(len(hist)),
                "gt_recent_opal_n": int(len(recent)),
                "gt_flip_share": share,
                "gt_route": route,
                "p_helios_v3_gt": float(1.0 - pa) if route else pa,
                "gt_top_policy": max(norm, key=norm.get),
            })
            rows.append(rec)
            if bool(r.opal_override):
                pending.append({
                    "end_utc": r.end_utc,
                    "success": bool(r.opal_rescue_success),
                    "votes": votes,
                })
    return pd.DataFrame(rows)

def add_v4(g0):
    rows = []
    for (part, win), g in g0.groupby(["partition","window"], sort=True):
        g = g.sort_values("start_utc").reset_index(drop=True)
        ext_hist, ext_pending = [], []
        active = False
        for r in g.itertuples(index=False):
            keep = []
            for item in ext_pending:
                if pd.Timestamp(item["end_utc"]) <= pd.Timestamp(r.start_utc):
                    ext_hist.append(item)
                else:
                    keep.append(item)
            ext_pending = keep

            recent = ext_hist[-RGE_WINDOW:]
            regret = int(sum(1 if x["success"] else -1 for x in recent))
            old = active
            if len(recent) >= RGE_WINDOW:
                if (not active) and regret >= RGE_ENTER:
                    active = True
                elif active and regret <= RGE_EXIT:
                    active = False

            base_route = bool(r.hard_route)
            expansion_candidate = bool(
                r.gate_active and r.opal_override and (not r.candidate_reversal)
            )
            expansion_route = bool(
                expansion_candidate and active and float(r.gt_flip_share) > RGE_THRESHOLD
            )
            route = bool(base_route or expansion_route)
            pa = float(r.p_aurora)
            p_v4 = float(1.0 - pa) if expansion_route else float(r.p_helios_v2)

            rec = r._asdict()
            rec.update({
                "rge_active": bool(active),
                "rge_state_changed": bool(active != old),
                "rge_matured_nonconsensus_n": int(len(ext_hist)),
                "rge_recent_n": int(len(recent)),
                "rge_recent_regret": int(regret),
                "rge_expansion_candidate": expansion_candidate,
                "rge_expansion_route": expansion_route,
                "v4_route": route,
                "p_helios_v4_rge": p_v4,
            })
            rows.append(rec)

            if bool(r.opal_override) and (not bool(r.candidate_reversal)):
                ext_pending.append({
                    "end_utc": r.end_utc,
                    "success": bool(r.opal_rescue_success),
                })
    return pd.DataFrame(rows)

def add_v5(g0):
    g = g0.copy()
    exc = (
        (~g.v4_route.astype(bool))
        & g.gate_active.astype(bool)
        & g.opal_override.astype(bool)
        & (~g.candidate_reversal.astype(bool))
        & g.gt_flip_share.astype(float).gt(DCE_GT)
        & g.active_expert.astype(str).eq("PATH_GLOBAL")
        & g.prob_path_superior.astype(float).gt(DCE_POSTERIOR)
    )
    g["dce_exception"] = exc
    g["v5_route"] = g.v4_route.astype(bool) | exc
    g["p_helios_v5_dce"] = g.p_helios_v4_rge.astype(float)
    g.loc[exc, "p_helios_v5_dce"] = 1.0 - g.loc[exc, "p_aurora"].astype(float)
    return g

def rescue_counts(g, col):
    y = g.y_up.astype(int)
    a = (g.p_aurora.astype(float) >= .5).astype(int)
    q = (g[col].astype(float) >= .5).astype(int)
    ch = a.ne(q)
    rescue = int((ch & a.ne(y) & q.eq(y)).sum())
    broken = int((ch & a.eq(y) & q.ne(y)).sum())
    return {
        "changed_n": int(ch.sum()),
        "rescued": rescue,
        "broken": broken,
        "net_rescue": rescue - broken,
    }

def summarize(g, period):
    rows = []
    for (part, win), z in g.groupby(["partition","window"], sort=True):
        ma = metric(z.y_up, z.p_aurora)
        vals = {
            "v1": metric(z.y_up, z.p_helios_v1_soft),
            "v2": metric(z.y_up, z.p_helios_v2),
            "v3": metric(z.y_up, z.p_helios_v3_gt),
            "v4": metric(z.y_up, z.p_helios_v4_rge),
            "v5": metric(z.y_up, z.p_helios_v5_dce),
        }
        rc = rescue_counts(z, "p_helios_v5_dce")
        rows.append({
            "period": period, "partition": part, "window": win,
            "common_n": int(len(z)),
            "candidate_n": int(z.candidate_reversal.sum()),
            "v1_route_n": int(z.hard_route.sum()),
            "v3_route_n": int(z.gt_route.sum()),
            "v4_route_n": int(z.v4_route.sum()),
            "v5_route_n": int(z.v5_route.sum()),
            "dce_exception_n": int(z.dce_exception.sum()),
            **rc,
            **{f"aurora_{k}": v for k, v in ma.items()},
            **{f"{name}_{k}": v for name, m in vals.items() for k, v in m.items()},
        })
    return pd.DataFrame(rows)

def development_gate(g):
    rows = []
    for (part, win), z in g[g.year.isin([2023, 2024])].groupby(["partition","window"], sort=True):
        reasons = []
        years_present = sorted(z.year.unique().tolist())
        if not (2023 in years_present and 2024 in years_present):
            reasons.append("MISSING_YEAR")
        ma = metric(z.y_up, z.p_aurora)
        mv = metric(z.y_up, z.p_helios_v5_dce)
        rc = rescue_counts(z, "p_helios_v5_dce")
        if int(z.v5_route.sum()) <= 0:
            reasons.append("NO_ROUTE")
        if rc["net_rescue"] <= 0:
            reasons.append("NET_RESCUE_NOT_POSITIVE")
        if mv["balanced_accuracy"] + 1e-12 < ma["balanced_accuracy"]:
            reasons.append("DEV_BA")
        if mv["brier"] > ma["brier"] + .003 + 1e-12:
            reasons.append("DEV_BRIER")
        for yr in [2023, 2024]:
            q = z[z.year.eq(yr)]
            if q.empty:
                continue
            ya = metric(q.y_up, q.p_aurora)
            yv = metric(q.y_up, q.p_helios_v5_dce)
            if yv["accuracy"] + .01 + 1e-12 < ya["accuracy"]:
                reasons.append(f"{yr}_ACC")
        rows.append({
            "partition": part, "window": win,
            "eligible": len(reasons) == 0,
            "reason": "PASS" if not reasons else "|".join(reasons),
            "n": int(len(z)),
            "aurora_ba": ma["balanced_accuracy"],
            "v5_ba": mv["balanced_accuracy"],
            "aurora_brier": ma["brier"],
            "v5_brier": mv["brier"],
            "v5_up_recall": mv["up_recall"],
            "v5_down_recall": mv["down_recall"],
            "v5_route_n": int(z.v5_route.sum()),
            **rc,
        })
    return pd.DataFrame(rows)

def stage4_status():
    raw = pd.read_csv(rift25.r0.RAW35, usecols=["dt_utc"])
    raw["dt_utc"] = pd.to_datetime(raw.dt_utc, utc=True, errors="coerce")
    raw_max = raw.dt_utc.max()

    targets = []
    for p in [rift25.r0.WGC, rift25.r0.SOB]:
        q = pd.read_csv(p, usecols=["start_utc","final_trainable"])
        q["start_utc"] = pd.to_datetime(q.start_utc, utc=True, errors="coerce")
        good = q.final_trainable.astype(str).str.lower().eq("true")
        targets.append(q[good])
    t = pd.concat(targets, ignore_index=True)
    y2026 = int(t.start_utc.dt.year.eq(2026).sum())
    tmax = t.start_utc.max()

    return {
        "status": "DATA_BLOCKED",
        "evidence_class": "2026_RETROSPECTIVE_STRESS_NOT_RUN",
        "reason": (
            "No corrected V5-equivalent SESSION target authority exists for a meaningful 2026 stress sample; "
            "the governed raw 15-minute archive used by the current session replay ends at the beginning of 2026. "
            "H3/daily labels are prohibited substitutes."
        ),
        "governed_raw15_max_utc": str(raw_max),
        "frozen_v5_target_max_start_utc": str(tmax),
        "frozen_v5_trainable_start_year_2026_rows": y2026,
        "selection_or_tuning_on_2026": False,
    }

def main():
    common = build_common_ledger()
    g = simulate_v1_v2(common)
    g = add_v3(g)
    g = add_v4(g)
    g = add_v5(g)

    dev = g[g.year.isin([2023, 2024])].copy()
    gate = development_gate(g)
    eligible = {
        (r.partition, r.window)
        for r in gate.itertuples(index=False)
        if bool(r.eligible)
    }
    tr = g[
        g.year.eq(2025)
        & g.apply(lambda r: (r.partition, r.window) in eligible, axis=1)
    ].copy()

    devm = summarize(dev, "STAGE2_DEV_2023_2024")
    trm = summarize(tr, "STAGE3_FROZEN_2025") if not tr.empty else pd.DataFrame()
    st4 = stage4_status()

    common.to_csv(OUT / "common_upstream_ledger.csv", index=False)
    g.to_csv(OUT / "helios_v1_v5_predictions_2023_2025.csv", index=False)
    devm.to_csv(OUT / "stage2_dev_metrics.csv", index=False)
    gate.to_csv(OUT / "stage2_eligibility.csv", index=False)
    trm.to_csv(OUT / "stage3_2025_metrics.csv", index=False)
    (OUT / "stage4_2026_status.json").write_text(json.dumps(st4, indent=2) + "\n")

    summary = {
        "status": "SESSION_HELIOS_V1_V5_STAGE4_REACHED",
        "lineage": "V1->V2->V3-GT->V4-RGE->V5-DCE",
        "common_rows_2023_2025": int(len(g)),
        "stage2_eligible_heads": [{"partition":p,"window":w} for p,w in sorted(eligible)],
        "stage2_gate": gate.to_dict("records"),
        "stage3_2025_metrics": trm.to_dict("records") if not trm.empty else [],
        "stage4_2026": st4,
        "guardrails": [
            "No historical H3 prediction/state CSV used as SESSION model input.",
            "Adaptive state is independent by partition/window.",
            "Only same-window rows with end_utc <= current start_utc mature into adaptive state.",
            "HELIOS thresholds/rules are inherited and not retuned.",
            "2025 is opened only for heads passing the preregistered 2023-2024 gate.",
            "2026 is not substituted with daily/H3 labels when SESSION source coverage is absent.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# SESSION HELIOS V1-V5 — STAGE-2→4 RESULT",
        "",
        "**Lineage:** V1 -> V2 -> V3-GT -> V4-RGE -> V5-DCE",
        "",
        "## Stage-2 — 2023-2024 development gate",
        "",
        "| Partition | Window | N | AURORA BA | V5 BA | AURORA Brier | V5 Brier | V5 UP | V5 DOWN | Routes | Rescue | Break | Net | Eligible | Reason |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in gate.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.n)} | "
            f"{100*r.aurora_ba:.2f}% | {100*r.v5_ba:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.v5_brier:.4f} | "
            f"{100*r.v5_up_recall:.2f}% | {100*r.v5_down_recall:.2f}% | "
            f"{int(r.v5_route_n)} | {int(r.rescued)} | {int(r.broken)} | {int(r.net_rescue):+d} | "
            f"{r.eligible} | {r.reason} |"
        )

    lines += ["", "## Stage-3 — frozen 2025 transport", ""]
    if trm.empty:
        lines.append("No HELIOS session head passed the preregistered Stage-2 gate; 2025 remained closed.")
    else:
        lines += [
            "| Partition | Window | N | AURORA BA | V5 BA | V5 Accuracy | V5 UP | V5 DOWN | V5 Brier | Routes | Rescue | Break | Net |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for r in trm.itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {int(r.common_n)} | "
                f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.v5_balanced_accuracy:.2f}% | "
                f"{100*r.v5_accuracy:.2f}% | {100*r.v5_up_recall:.2f}% | "
                f"{100*r.v5_down_recall:.2f}% | {r.v5_brier:.4f} | "
                f"{int(r.v5_route_n)} | {int(r.rescued)} | {int(r.broken)} | {int(r.net_rescue):+d} |"
            )

    lines += [
        "",
        "## Stage-4 — 2026 retrospective stress",
        "",
        f"**Status:** {st4['status']}",
        "",
        st4["reason"],
        "",
        f"- governed raw 15m max: {st4['governed_raw15_max_utc']}",
        f"- frozen V5 target max start: {st4['frozen_v5_target_max_start_utc']}",
        f"- frozen V5 trainable rows starting in 2026: {st4['frozen_v5_trainable_start_year_2026_rows']}",
        "- 2026 was not used for selection or tuning.",
    ]
    (OUT / "result.md").write_text("\n".join(lines) + "\n")
    print((OUT / "result.md").read_text())

if __name__ == "__main__":
    main()
