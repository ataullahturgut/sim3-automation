from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
WARM = AX / "GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
WGC = AX / "GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB = AX / "GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
OUT = AX / "SESSION_MODEL02_SHALLOW_CART_VARSEL_OUT"
OUT.mkdir(exist_ok=True)

STAK_REPO = "lbruton/StakTrakr"
STAK_REF = "54fdf1c8d39b7b6c7b874d0f30f784296e886044"
YEARS = range(2010, 2026)

SEED = 20261007
BLOCK = 5
MIN_OUTER_TRAIN = 240
INNER_MIN_TRAIN = 180
INNER_VAL = 30
MAX_SELECTED = 6
MIN_SELECTED = 3
MAX_AGE_DAYS = 7

GOLD = ["gold_r1", "gold_r5", "gold_r21", "sigma20"]
METALS = [
    "silver_r1", "silver_r5", "silver_r21",
    "platinum_r1", "platinum_r5", "platinum_r21",
    "palladium_r1", "palladium_r5", "palladium_r21",
]
EQUITIES = [
    "nasdaq_r1", "nasdaq_r5", "nasdaq_r21",
    "sp500_r1", "sp500_r5", "sp500_r21",
    "djia_r1", "djia_r5", "djia_r21",
]
CANDIDATES = GOLD + METALS + EQUITIES

METAL_LABELS = {
    "gold": "Gold",
    "silver": "Silver",
    "platinum": "Platinum",
    "palladium": "Palladium",
}
EQUITY_IDS = {
    "nasdaq": "NASDAQ100_FRED",
    "sp500": "SP500_FRED",
    "djia": "DJIA_FRED",
}

def tree():
    return DecisionTreeClassifier(
        criterion="log_loss",
        max_depth=3,
        min_samples_leaf=60,
        random_state=SEED,
    )

def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }

def predict_prob(m, X):
    pp = m.predict_proba(X)
    if pp.shape[1] == 1:
        return np.repeat(float(m.classes_[0]), len(X))
    return pp[:, list(m.classes_).index(1)]

def get_bytes(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "gold-session-cart-varsel/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def load_metal_features():
    raw_by_metal = defaultdict(list)
    hashes = {}
    for year in YEARS:
        url = f"https://raw.githubusercontent.com/{STAK_REPO}/{STAK_REF}/data/spot-history-{year}.json"
        raw = get_bytes(url)
        hashes[str(year)] = hashlib.sha256(raw).hexdigest()
        rows = json.loads(raw)
        for rec in rows:
            metal = str(rec.get("metal") or "")
            key = next((k for k, v in METAL_LABELS.items() if v == metal), None)
            if key is None:
                continue
            ts = pd.to_datetime(rec.get("timestamp"), errors="coerce")
            try:
                value = float(rec.get("spot"))
            except Exception:
                continue
            if pd.isna(ts) or not np.isfinite(value) or value <= 0:
                continue
            d = ts.normalize()
            if d.weekday() >= 5:
                continue
            raw_by_metal[key].append((d, value))

    out = {}
    for key in METAL_LABELS:
        q = pd.DataFrame(raw_by_metal[key], columns=["obs_date", "value"])
        q = q.sort_values("obs_date").drop_duplicates("obs_date", keep="last")
        lv = np.log(q["value"].astype(float))
        for h in [1, 5, 21]:
            q[f"{key}_r{h}"] = lv.diff(h)
        if key == "gold":
            q["sigma20"] = lv.diff().rolling(20).std(ddof=0)
            keep = ["obs_date", "gold_r1", "gold_r5", "gold_r21", "sigma20"]
        else:
            keep = ["obs_date", f"{key}_r1", f"{key}_r5", f"{key}_r21"]
        out[key] = q[keep].dropna().reset_index(drop=True)
    return out, hashes

def load_equity_features():
    dsn = os.environ["NEON_DATABASE_URL"]
    out = {}
    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for key, sid in EQUITY_IDS.items():
                cur.execute(
                    """
                    SELECT observation_ts::date, value, retrieved_at
                    FROM observations
                    WHERE series_id=%s
                    ORDER BY observation_ts, retrieved_at
                    """,
                    (sid,),
                )
                rows = cur.fetchall()
                if not rows:
                    raise RuntimeError(f"NO_ROWS {sid}")
                q = pd.DataFrame(rows, columns=["obs_date", "value", "retrieved_at"])
                q["obs_date"] = pd.to_datetime(q["obs_date"])
                q["value"] = pd.to_numeric(q["value"], errors="coerce")
                q = (
                    q.dropna(subset=["value"])
                    .sort_values(["obs_date", "retrieved_at"])
                    .drop_duplicates("obs_date", keep="last")
                )
                q = q[q["value"] > 0].copy()
                lv = np.log(q["value"].astype(float))
                for h in [1, 5, 21]:
                    q[f"{key}_r{h}"] = lv.diff(h)
                out[key] = q[["obs_date", f"{key}_r1", f"{key}_r5", f"{key}_r21"]].dropna()
        conn.rollback()
    return out

def load_targets():
    frames = []
    w = pd.read_csv(WARM)
    w = w[w["final_trainable"].astype(str).str.lower().eq("true")].copy()
    frames.append(w)
    for p in [WGC, SOB]:
        q = pd.read_csv(p)
        q = q[q["final_trainable"].astype(str).str.lower().eq("true")].copy()
        frames.append(q)
    t = pd.concat(frames, ignore_index=True, sort=False)
    t["start_utc"] = pd.to_datetime(t["start_utc"], utc=True)
    t["end_utc"] = pd.to_datetime(t["end_utc"], utc=True)
    t["year"] = t["start_utc"].dt.year
    t["y_up"] = (t["direction"] == "UP").astype(int)
    t["start_ny"] = t["start_utc"].dt.tz_convert("America/New_York")
    t["start_ny_date"] = t["start_ny"].dt.tz_localize(None).dt.normalize()
    t["daily_cutoff_date"] = t["start_ny_date"] - pd.Timedelta(days=1)
    return t.sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)

def asof_source(panel, src, prefix):
    q = src.copy().sort_values("obs_date")
    q = q.rename(columns={"obs_date": f"{prefix}_obs_date"})
    panel = pd.merge_asof(
        panel.sort_values("daily_cutoff_date"),
        q.sort_values(f"{prefix}_obs_date"),
        left_on="daily_cutoff_date",
        right_on=f"{prefix}_obs_date",
        direction="backward",
    )
    panel[f"{prefix}_age_days"] = (
        panel["start_ny_date"] - panel[f"{prefix}_obs_date"]
    ).dt.days
    return panel

def build_panel():
    metals, hashes = load_metal_features()
    equities = load_equity_features()
    p = load_targets().copy()
    for key in ["gold", "silver", "platinum", "palladium"]:
        p = asof_source(p, metals[key], key)
    for key in ["nasdaq", "sp500", "djia"]:
        p = asof_source(p, equities[key], key)

    age_cols = [f"{k}_age_days" for k in ["gold", "silver", "platinum", "palladium", "nasdaq", "sp500", "djia"]]
    p = p.dropna(subset=CANDIDATES + age_cols + ["direction"]).copy()
    for c in age_cols:
        if (p[c] < 1).any():
            raise RuntimeError(f"SAME_DAY_FEATURE_LEAK {c}")
    p["max_daily_age_days"] = p[age_cols].max(axis=1)
    p = p[p["max_daily_age_days"] <= MAX_AGE_DAYS].copy()
    return p.sort_values(["partition", "window", "start_utc"]).reset_index(drop=True), hashes

def fit_predict(tr, te, features):
    m = tree()
    m.fit(tr[features].astype(float).to_numpy(), tr["y_up"].to_numpy(int))
    return m, predict_prob(m, te[features].astype(float).to_numpy())

def inner_feature_analysis(tr):
    tr = tr.sort_values("start_utc").reset_index(drop=True)
    possible = min(3, (len(tr) - INNER_MIN_TRAIN) // INNER_VAL)
    if possible < 2:
        return None
    val_starts = [len(tr) - possible * INNER_VAL + i * INNER_VAL for i in range(possible)]
    stat = {f: {"used": 0, "pos": 0, "ba": [], "brier": []} for f in CANDIDATES}
    valid_folds = 0

    for fold_id, pos in enumerate(val_starts):
        va = tr.iloc[pos:pos + INNER_VAL].copy()
        if va.empty:
            continue
        cut = va["start_utc"].min()
        it = tr[(tr["end_utc"] <= cut) & (tr["start_utc"] < cut)].copy()
        if len(it) < INNER_MIN_TRAIN or it["y_up"].nunique() < 2:
            continue

        m, p0 = fit_predict(it, va, CANDIDATES)
        base = metrics(va["y_up"], p0)
        used_ids = m.tree_.feature[m.tree_.feature >= 0]
        used = Counter(CANDIDATES[int(i)] for i in used_ids)
        for f in used:
            stat[f]["used"] += 1

        for j, f in enumerate(CANDIDATES):
            if f not in used:
                stat[f]["ba"].append(0.0)
                stat[f]["brier"].append(0.0)
                continue
            ba_imp = []
            br_imp = []
            for rep in range(3):
                vv = va[CANDIDATES].astype(float).copy()
                rng = np.random.default_rng(SEED + fold_id * 10000 + j * 100 + rep)
                vals = vv[f].to_numpy().copy()
                rng.shuffle(vals)
                vv[f] = vals
                pp = predict_prob(m, vv.to_numpy())
                mm = metrics(va["y_up"], pp)
                ba_imp.append(base["balanced_accuracy"] - mm["balanced_accuracy"])
                br_imp.append(mm["brier"] - base["brier"])
            mba = float(np.mean(ba_imp))
            mbr = float(np.mean(br_imp))
            stat[f]["ba"].append(mba)
            stat[f]["brier"].append(mbr)
            if mba > 0 or mbr > 0:
                stat[f]["pos"] += 1
        valid_folds += 1

    if valid_folds < 2:
        return None

    rows = []
    need = int(np.ceil(valid_folds / 2))
    for f in CANDIDATES:
        ba = stat[f]["ba"]
        br = stat[f]["brier"]
        rows.append({
            "feature": f,
            "valid_folds": valid_folds,
            "used_folds": int(stat[f]["used"]),
            "positive_folds": int(stat[f]["pos"]),
            "median_ba_importance": float(np.median(ba)) if ba else 0.0,
            "median_brier_importance": float(np.median(br)) if br else 0.0,
            "mean_ba_importance": float(np.mean(ba)) if ba else 0.0,
            "mean_brier_importance": float(np.mean(br)) if br else 0.0,
        })
    rank = pd.DataFrame(rows)
    rank["stable"] = (
        (rank["used_folds"] >= need)
        & (rank["positive_folds"] >= need)
        & ((rank["median_ba_importance"] > 0) | (rank["median_brier_importance"] > 0))
    )
    rank = rank.sort_values(
        ["stable", "used_folds", "positive_folds", "median_ba_importance", "median_brier_importance"],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)

    selected = rank.loc[rank["stable"], "feature"].tolist()[:MAX_SELECTED]
    if len(selected) < MIN_SELECTED:
        for f in rank.loc[rank["used_folds"] > 0, "feature"]:
            if f not in selected:
                selected.append(f)
            if len(selected) >= MIN_SELECTED:
                break
    if not selected:
        selected = GOLD.copy()
    return selected[:MAX_SELECTED], rank

def replay_dev_window(g, part, win):
    g = g.sort_values("start_utc").reset_index(drop=True)
    test = g[g["year"].isin([2023, 2024])].copy().reset_index(drop=True)
    pred_rows = []
    sel_rows = []

    for bs in range(0, len(test), BLOCK):
        te = test.iloc[bs:bs + BLOCK].copy()
        if te.empty:
            continue
        cut = te["start_utc"].min()
        tr = g[(g["end_utc"] <= cut) & (g["start_utc"] < cut)].copy()
        if len(tr) < MIN_OUTER_TRAIN or tr["y_up"].nunique() < 2:
            continue
        sf = inner_feature_analysis(tr)
        if sf is None:
            continue
        selected, ranking = sf

        models = {
            "SELECTED_CART": selected,
            "GOLD_ONLY_CART": GOLD,
            "FULL_LEGACY_CART": CANDIDATES,
        }
        for model_name, feats in models.items():
            m, pp = fit_predict(tr, te, feats)
            for r, p in zip(te.itertuples(index=False), pp):
                pred_rows.append({
                    "representation": model_name,
                    "partition": part,
                    "window": win,
                    "label_date": r.label_date,
                    "start_utc": r.start_utc,
                    "end_utc": r.end_utc,
                    "year": int(r.year),
                    "y_up": int(r.y_up),
                    "p_up": float(p),
                    "train_n": int(len(tr)),
                    "outer_block": int(bs // BLOCK),
                    "selected_features": "|".join(selected) if model_name == "SELECTED_CART" else "|".join(feats),
                })

        for rr in ranking.itertuples(index=False):
            sel_rows.append({
                "partition": part,
                "window": win,
                "outer_block": int(bs // BLOCK),
                "outer_year": int(te["year"].iloc[0]),
                "outer_start": str(te["start_utc"].min()),
                "feature": rr.feature,
                "selected": int(rr.feature in selected),
                "valid_folds": int(rr.valid_folds),
                "used_folds": int(rr.used_folds),
                "positive_folds": int(rr.positive_folds),
                "median_ba_importance": float(rr.median_ba_importance),
                "median_brier_importance": float(rr.median_brier_importance),
            })

    return pd.DataFrame(pred_rows), pd.DataFrame(sel_rows)

def aggregate_metrics(pred, period):
    rows = []
    for (rep, part, win), z in pred.groupby(["representation", "partition", "window"], sort=True):
        rows.append({"period": period, "representation": rep, "partition": part, "window": win, **metrics(z["y_up"], z["p_up"])})
    return pd.DataFrame(rows)

def choose_freeze(dev_metrics, sel_log, part, win):
    m = dev_metrics[(dev_metrics["partition"] == part) & (dev_metrics["window"] == win)].copy()
    m["admissible"] = (m["up_recall"] >= 0.30) & (m["down_recall"] >= 0.30) & (m["n"] >= 80)
    pool = m[m["admissible"]].copy()
    status = "ADMISSIBLE"
    if pool.empty:
        pool = m.copy()
        status = "NO_ADMISSIBLE_REPRESENTATION"

    best_ba = float(pool["balanced_accuracy"].max())
    near = pool[pool["balanced_accuracy"] >= best_ba - 0.01].copy()
    complexity = {"GOLD_ONLY_CART": 4, "FULL_LEGACY_CART": len(CANDIDATES), "SELECTED_CART": 6}
    near["complexity"] = near["representation"].map(complexity)
    near = near.sort_values(["brier", "complexity", "balanced_accuracy"], ascending=[True, True, False])
    winner = str(near.iloc[0]["representation"])

    if winner == "GOLD_ONLY_CART":
        feats = GOLD.copy()
    elif winner == "FULL_LEGACY_CART":
        feats = CANDIDATES.copy()
    else:
        q = sel_log[(sel_log["partition"] == part) & (sel_log["window"] == win) & (sel_log["selected"] == 1)].copy()
        if q.empty:
            feats = GOLD.copy()
        else:
            blocks = q[["outer_block", "outer_year"]].drop_duplicates()
            nb = max(1, len(blocks))
            counts = q.groupby("feature").size().rename("count")
            years = q.groupby("feature")["outer_year"].nunique().rename("years")
            avg_ba = q.groupby("feature")["median_ba_importance"].mean().rename("avg_ba")
            avg_br = q.groupby("feature")["median_brier_importance"].mean().rename("avg_br")
            s = pd.concat([counts, years, avg_ba, avg_br], axis=1).fillna(0).reset_index()
            s["freq"] = s["count"] / nb
            s["both_years"] = s["years"] >= 2
            s = s.sort_values(["both_years", "freq", "avg_ba", "avg_br"], ascending=[False, False, False, False])
            stable = s[(s["freq"] >= 0.20) & s["both_years"]]["feature"].tolist()
            feats = stable[:MAX_SELECTED]
            if len(feats) < MIN_SELECTED:
                for f in s["feature"]:
                    if f not in feats:
                        feats.append(f)
                    if len(feats) >= MIN_SELECTED:
                        break
            feats = feats[:MAX_SELECTED]
    return winner, feats, status

def replay_2025_window(g, part, win, features):
    g = g.sort_values("start_utc").reset_index(drop=True)
    teall = g[g["year"].isin([2023, 2024, 2025])].copy().reset_index(drop=True)
    rows = []
    for bs in range(0, len(teall), BLOCK):
        te = teall.iloc[bs:bs + BLOCK].copy()
        if te.empty:
            continue
        cut = te["start_utc"].min()
        tr = g[(g["end_utc"] <= cut) & (g["start_utc"] < cut)].copy()
        if len(tr) < MIN_OUTER_TRAIN or tr["y_up"].nunique() < 2:
            continue
        m, pp = fit_predict(tr, te, features)
        for r, p in zip(te.itertuples(index=False), pp):
            if int(r.year) != 2025:
                continue
            rows.append({
                "representation": "FROZEN_CART",
                "partition": part,
                "window": win,
                "label_date": r.label_date,
                "start_utc": r.start_utc,
                "end_utc": r.end_utc,
                "year": 2025,
                "y_up": int(r.y_up),
                "p_up": float(p),
                "train_n": int(len(tr)),
                "continuous_block": int(bs // BLOCK),
                "frozen_features": "|".join(features),
            })
    return pd.DataFrame(rows)

def main():
    panel, hashes = build_panel()
    dev_preds = []
    sel_logs = []

    for (part, win), g in panel.groupby(["partition", "window"], sort=True):
        p, s = replay_dev_window(g, part, win)
        if not p.empty:
            dev_preds.append(p)
        if not s.empty:
            sel_logs.append(s)

    dev_pred = pd.concat(dev_preds, ignore_index=True)
    sel_log = pd.concat(sel_logs, ignore_index=True)
    dev_met = aggregate_metrics(dev_pred, "DEV_2023_2024")

    freeze = []
    for (part, win), _ in panel.groupby(["partition", "window"], sort=True):
        winner, feats, status = choose_freeze(dev_met, sel_log, part, win)
        freeze.append({
            "partition": part,
            "window": win,
            "development_winner": winner,
            "freeze_status": status,
            "frozen_features": feats,
            "n_features": len(feats),
        })

    transport = []
    for item in freeze:
        g = panel[(panel["partition"] == item["partition"]) & (panel["window"] == item["window"])].copy()
        z = replay_2025_window(g, item["partition"], item["window"], item["frozen_features"])
        if not z.empty:
            transport.append(z)
    tr_pred = pd.concat(transport, ignore_index=True)
    tr_met = aggregate_metrics(tr_pred, "FROZEN_SPEC_2025")

    OUT.mkdir(exist_ok=True)
    dev_pred.to_csv(OUT / "dev_predictions.csv", index=False)
    sel_log.to_csv(OUT / "dev_variable_selection.csv", index=False)
    dev_met.to_csv(OUT / "dev_metrics.csv", index=False)
    tr_pred.to_csv(OUT / "transport_2025_predictions.csv", index=False)
    tr_met.to_csv(OUT / "transport_2025_metrics.csv", index=False)
    (OUT / "frozen_features.json").write_text(json.dumps(freeze, indent=2) + "\n")

    summary = {
        "status": "SESSION_MODEL02_SHALLOW_CART_VARIABLE_SELECTION_COMPLETE",
        "model": {
            "estimator": "DecisionTreeClassifier",
            "criterion": "log_loss",
            "max_depth": 3,
            "min_samples_leaf": 60,
            "threshold": 0.5,
        },
        "candidate_universe": CANDIDATES,
        "source_ready_rule": "latest observation from a strictly earlier America/New_York calendar date; max source age 7 days",
        "chronology": "2022 warm-up; 2023-2024 development/selection; 2025 frozen-specification causal transport; 2026 unopened",
        "variable_selection": {
            "outer_block": BLOCK,
            "min_outer_train": MIN_OUTER_TRAIN,
            "inner_min_train": INNER_MIN_TRAIN,
            "inner_validation_rows": INNER_VAL,
            "inner_folds": "2-3 chronological",
            "max_selected": MAX_SELECTED,
            "min_selected": MIN_SELECTED,
            "importance": "held-out permutation contribution to Balanced Accuracy and Brier plus split-use stability",
        },
        "freeze": freeze,
        "development_metrics": dev_met.to_dict("records"),
        "transport_2025_metrics": tr_met.to_dict("records"),
        "stak_ref": STAK_REF,
        "stak_annual_sha256": hashes,
        "guardrails": [
            "No DAILY/H3 target used.",
            "No 2025 outcome used for feature selection or representation choice.",
            "No 2026 outcome opened.",
            "No archived model prediction/state used as a feature.",
            "Tree depth/min-leaf/threshold are fixed from the legacy Shallow CART identity.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# SESSION MODEL-02 — SHALLOW CART — VARIABLE-SELECTION RESULT",
        "",
        "**Status:** variable analysis and frozen 2025 transport completed.",
        "",
        "## Frozen per-session variables",
        "",
        "| Partition | Window | DEV winner | Frozen variables |",
        "|---|---|---|---|",
    ]
    for x in freeze:
        lines.append(f"| {x['partition']} | {x['window']} | {x['development_winner']} | {', '.join(x['frozen_features'])} |")
    lines += [
        "",
        "## 2025 frozen-specification transport",
        "",
        "| Partition | Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in tr_met.sort_values(["partition", "window"]).itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.n)} | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | "
            f"{100*r.down_recall:.2f}% | {r.brier:.4f} |"
        )
    lines += [
        "",
        "Feature selection used only 2022 warm-up and 2023-2024 matured development history. "
        "2025 was opened only after the per-session representation was frozen; 2026 was not used.",
    ]
    (OUT / "result.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2, default=str))

if __name__ == "__main__":
    main()
