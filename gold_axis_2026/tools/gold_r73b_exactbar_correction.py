"""R73B — exact-bar CME alignment correction of R73 (model frozen).

Prereg: gold_axis_2026/GOLD_R73B_20261012_OVN1645_XMKT_RESIDUAL_EXACT_BAR_CORRECTION_PREREG.md (a6f716ed).
Reuses the unchanged R73 model/evaluation code (tools/gold_r73_ovn1645_xmkt_residual_reversal.py):
ridge alpha=10, rolling 250, min 60, ZN/NQ/CL, sign(-residual), same gates H1/H2/H3.

Inputs
  v1 panel: GOLD_R73_20261012_OVN1645_XMKT_PANEL_LOGRET_E5.csv           (original, unchanged)
  v2 panel: GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_PANEL_LOGRET_E5.csv  (exact bars; = v1 with
            non-exact CME cells set to NULL, verified in SQL; full7 = all 06-12 UTC bars present)
Outputs
  GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_ROWS.csv
  GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_SUMMARY.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gold_r73_ovn1645_xmkt_residual_reversal as r73  # noqa: E402

ROOT = r73.ROOT
V1 = r73.PANEL
V2 = ROOT / "GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_PANEL_LOGRET_E5.csv"
OUT_ROWS = ROOT / "GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_ROWS.csv"
OUT_SUMMARY = ROOT / "GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_SUMMARY.json"
CME = ["zn7", "nq7", "cl7", "zn3", "nq3", "cl3"]


def load(path, full7_only=False):
    df = pd.read_csv(path, parse_dates=["decision_date"])
    df["year"] = df.decision_date.dt.year
    df["isodow"] = df.decision_date.dt.isocalendar().day.astype(int)
    if full7_only:
        df.loc[df.full7 == 0, CME] = np.nan
    return df


def eligible(df):
    tgt = (df.isodow <= 4) & df.ovn.notna()
    e = {str(k): int(v) for k, v in df[tgt].groupby("year").size().items()}
    e["DEV_2023_2024"] = e.get("2023", 0) + e.get("2024", 0)
    return e


def gates(summary):
    w7 = summary["W7"]["per_year"]["DEV_2023_2024"]
    w3 = summary["W3"]["per_year"]["DEV_2023_2024"]
    h7, h3 = r73.holm([w7["binom_p_resid_acc_gt_50"], w3["binom_p_resid_acc_gt_50"]])
    H1 = h7 < 0.05 and w7["R_RESID"]["ba"] > 0.5
    H2 = w7["RESID_vs_REV"]["one_sided_p"] < 0.05
    ols = summary["W7"]["dev"]["ols_ovn_on_fitted_resid_hc3"]
    H3 = ols["coef"]["resid"] < 0 and ols["one_sided_p_resid_lt_0"] < 0.05
    verdict = ("CONTINUE" if H1 and H2 and H3 else "RAW-REVERSAL-ONLY" if H1 and H3
               else "REJECT" if not H1 else "INCONCLUSIVE / MORE DATA")
    return {"H1_holm_p_W7": h7, "H1_holm_p_W3": h3, "H1": H1, "H2": H2, "H3": H3, "verdict_primary_W7": verdict}


def run_variant(df):
    out, rows = {}, []
    elig = eligible(df)
    for w in (7, 3):
        rw = r73.build_rows(df, w)
        ev = r73.evaluate(rw, elig)
        ev["r67_matched"] = r73.r67_compare(rw)
        out[f"W{w}"] = ev
        rows.append(rw)
    out["eligible_target_nights_mon_thu"] = elig
    out["gates"] = gates(out)
    return out, pd.concat(rows)


def common_date_decomposition(rv1, rv2):
    res = {}
    for w in ("W7", "W3"):
        a = rv1[rv1.window == w].set_index("decision_date")
        b = rv2[rv2.window == w].set_index("decision_date")
        for yr in sorted(set(a.year) | set(b.year)) + ["DEV_2023_2024"]:
            ys = (2023, 2024) if yr == "DEV_2023_2024" else (yr,)
            A, B = a[a.year.isin(ys)], b[b.year.isin(ys)]
            com = A.index.intersection(B.index)
            drop = A.index.difference(B.index)
            add = B.index.difference(A.index)
            ac, bc = A.loc[com], B.loc[com]
            changed = ac.p_resid != bc.p_resid
            res[f"{w}_{yr}"] = {
                "n_v1": len(A), "n_v2": len(B), "common": len(com), "dropped_in_v2": len(drop), "added_in_v2": len(add),
                "v1_correct_on_dropped": int((A.loc[drop].p_resid == A.loc[drop].y).sum()),
                "v1_correct_on_common": int((ac.p_resid == ac.y).sum()),
                "v2_correct_on_common": int((bc.p_resid == bc.y).sum()),
                "prediction_changed_on_common": int(changed.sum()),
                "changed_v2_right_v1_wrong": int((changed & (bc.p_resid == bc.y)).sum()),
                "changed_v1_right_v2_wrong": int((changed & (ac.p_resid == ac.y)).sum()),
                "max_abs_resid_diff_common_e5": float((ac.resid - bc.resid).abs().max()) if len(com) else None,
            }
    return res


def source_mixing(df, w=7):
    """Training-row source composition for each 2026 prediction, and a same-source-only re-score."""
    g, f = f"g{w}", [f"zn{w}", f"nq{w}", f"cl{w}"]
    ok = df[[g] + f].notna().all(axis=1)
    tr = df.loc[ok, ["decision_date", "xau_source", g] + f].reset_index(drop=True)
    tgt = (df.isodow <= 4) & df.ovn.notna() & (df.ovn != 0) & ok & (df.year == 2026)
    comp, same = [], []
    for idx in df.index[tgt]:
        r = df.loc[idx]
        past = tr[tr.decision_date < r.decision_date].tail(r73.WINDOW)
        n_ev = int((past.xau_source != r.xau_source).sum())
        comp.append({"decision_date": r.decision_date.date().isoformat(), "n_train": len(past), "n_other_source": n_ev})
        ps = tr[(tr.decision_date < r.decision_date) & (tr.xau_source == r.xau_source)].tail(r73.WINDOW)
        if len(ps) < r73.MIN_TRAIN or float(r[g]) == 0:
            continue
        X, y = ps[f].to_numpy(float), ps[g].to_numpy(float)
        mu, sd = X.mean(0), X.std(0)
        Z = (X - mu) / sd
        b = np.linalg.solve(Z.T @ Z + r73.ALPHA * np.eye(3), Z.T @ (y - y.mean()))
        e = float(r[g]) - float(y.mean() + ((r[f].to_numpy(float) - mu) / sd) @ b)
        same.append({"decision_date": r.decision_date.date().isoformat(), "resid_same_src": e,
                     "p_resid_same_src": int(e < 0)})
    return pd.DataFrame(comp), pd.DataFrame(same)


def main():
    v1, v2 = load(V1), load(V2)
    v2f = load(V2, full7_only=True)
    s_v1, rows_v1 = run_variant(v1)
    s_v2, rows_v2 = run_variant(v2)
    s_f7, rows_f7 = run_variant(v2f)

    comp, same = source_mixing(v2)
    base26 = rows_v2[(rows_v2.window == "W7") & (rows_v2.year == 2026)].merge(same, on="decision_date", how="inner")
    y = base26.y.to_numpy()
    mixed_months = comp[comp.n_other_source > 0]
    src = {
        "w7_2026_predictions": len(comp),
        "predictions_with_any_2025_evduka_training_rows": int((comp.n_other_source > 0).sum()),
        "first_date": comp.decision_date.min(), "last_date_with_mixing": mixed_months.decision_date.max() if len(mixed_months) else None,
        "evduka_rows_in_training_first_2026_prediction": int(comp.n_other_source.iloc[0]) if len(comp) else None,
        "total_training_rows_summed": int(comp.n_train.sum()), "evduka_training_rows_summed": int(comp.n_other_source.sum()),
        "same_source_rescore_common_n": len(base26),
        "mixed_training_on_common": r73.rule_metrics(y, base26.p_resid, base26.ovn, base26.lc, base26.sc),
        "same_source_training_on_common": r73.rule_metrics(y, base26.p_resid_same_src, base26.ovn, base26.lc, base26.sc),
        "prediction_changed": int((base26.p_resid != base26.p_resid_same_src).sum()),
        "mcnemar_same_src_vs_mixed": r73.mcnemar(y, base26.p_resid_same_src, base26.p_resid),
        "spearman_resid_mixed_vs_same": float(pd.Series(base26.resid).rank().corr(pd.Series(base26.resid_same_src).rank())),
    }

    summary = {"prereg_commit": "a6f716ed3803ec9faec5387b488dd62433ab98e3",
               "original_r73_prereg_commit": "2371b588f51422196f9341fe5605c5a97f3d43a5",
               "params_unchanged": dict(alpha=r73.ALPHA, window=r73.WINDOW, min_train=r73.MIN_TRAIN),
               "V1_original_rerun": s_v1, "V2_exact_bar_primary": s_v2, "S_FULL7": s_f7,
               "common_date_decomposition_v1_vs_v2": common_date_decomposition(rows_v1, rows_v2),
               "S_SRC_2026_source_mixing": src}
    rows_v2.assign(variant="V2_exact_bar").to_csv(OUT_ROWS, index=False, float_format="%.4f")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=1, default=float))
    json.dump({"V1": s_v1["gates"], "V2": s_v2["gates"], "S_FULL7": s_f7["gates"]}, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
