"""Deterministic, read-only PRAMV continuation coverage audit.

Inputs: existing, governed 2026-10-07 CSVs. Does NOT refit frozen PRAMV V1
or change its threshold, time window, or feature set.
Output is a new 2026-10-08 diagnostic CSV; not an OOS promotion.
"""
from pathlib import Path
import numpy as np
import pandas as pd

AX = Path(__file__).resolve().parents[1]
FS = AX / "GOLD_EXECUTION_FSMR_STAGE4_PREDICTIONS_2026-10-07.csv"
PS = AX / "GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv"
BA = AX / "GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
LI = AX / "GOLD_EXECUTION_LIT_STAGE2_PREDICTIONS_2026-10-07.csv"
OUT = AX / "GOLD_EXECUTION_CONTINUATION_EXPANSION_METRICS_2026-10-08.csv"

def load():
    f = pd.read_csv(FS, dtype={"state": str})
    f = f[f.model.eq("FSMR4")][["date", "year", "state"]]
    p = pd.read_csv(PS)
    p = p[p.family.eq("M4_SIG_FPCA_MACRO")][["date", "pred", "p_up", "ret_target"]]
    p = p.rename(columns={"pred": "m4_pred", "p_up": "m4_prob"})
    b = pd.read_csv(BA)
    b = b[b.policy.eq("PAIR_ALL")][["date", "year", "pred", "y", "macro_released"]]
    b = b.rename(columns={"pred": "pair_pred"})
    l = pd.read_csv(LI)
    l = l[l.spec.eq("BASE_1600_1630")][["date", "pred_logit"]]
    l = l.rename(columns={"pred_logit": "base_pred"})
    q = (b.merge(f, on=["date", "year"], validate="one_to_one")
           .merge(p, on="date", validate="one_to_one")
           .merge(l, on="date", validate="one_to_one")
           .sort_values("date").reset_index(drop=True))
    assert q.date.is_unique
    q["no_macro"] = q.macro_released.astype(int).eq(0)
    q["is_cont"] = q.state.isin(["00", "11"])
    q["is_reversal"] = q.state.isin(["01", "10"])
    assert q.is_cont.ne(q.is_reversal).all()
    q["rfr"] = np.where(q.state.eq("10"), 1, np.where(q.state.eq("01"), 0, -1))
    q["cont_sign"] = np.where(q.state.eq("11"), 1, np.where(q.state.eq("00"), 0, -1))
    assert q.groupby("year").size().to_dict() == {2023:255,2024:259,2025:253}
    return q

def policies(q):
    z = pd.DataFrame(index=q.index)
    z["PRAMV_V1"] = q.rfr.where(q.is_reversal & q.no_macro & q.rfr.eq(q.m4_pred))
    a = q.is_cont & q.no_macro
    z["PRAMV_PLUS_CONT_SIGN"] = z.PRAMV_V1.fillna(q.cont_sign.where(a))
    z["PRAMV_PLUS_CONT_M4"] = z.PRAMV_V1.fillna(q.m4_pred.where(a))
    z["PRAMV_PLUS_CONT_PAIR"] = z.PRAMV_V1.fillna(q.pair_pred.where(a))
    z["PRAMV_PLUS_CONT_BASE"] = z.PRAMV_V1.fillna(q.base_pred.where(a))
    z["PRAMV_PLUS_CONT_M4_PAIR_AGREE"] = z.PRAMV_V1.fillna(q.m4_pred.where(a & q.m4_pred.eq(q.pair_pred)))
    z["PRAMV_PLUS_CONT_M4_BASE_AGREE"] = z.PRAMV_V1.fillna(q.m4_pred.where(a & q.m4_pred.eq(q.base_pred)))
    z["PRAMV_PLUS_CONT_11_UP_ONLY"] = z.PRAMV_V1.fillna(pd.Series(1, index=q.index).where(a & q.state.eq("11")))
    return z

def metric(g, pred):
    p = pred.dropna().astype(int)
    y = g.loc[p.index, "y"].astype(int)
    r = g.loc[p.index, "ret_target"].astype(float)
    n = len(p)
    tp = int(((p == 1) & (y == 1)).sum())
    tn = int(((p == 0) & (y == 0)).sum())
    fp = int(((p == 1) & (y == 0)).sum())
    fn = int(((p == 0) & (y == 1)).sum())
    return {"n": n, "correct": tp + tn,
            "accuracy": (tp+tn)/n if n else np.nan,
            "BA": (tp/(tp+fn)+tn/(tn+fp))/2 if tp+fn and tn+fp else np.nan,
            "up_recall": tp/(tp+fn) if tp+fn else np.nan,
            "down_recall": tn/(tn+fp) if tn+fp else np.nan,
            "up_predictions": int((p == 1).sum()),
            "zero_cost_signed_log_return_sum_diagnostic_only": float((r*(2*p-1)).sum())}

def main():
    q = load()
    p = policies(q)
    results = []
    for year in (2023, 2024, 2025):
        mask = q.year.eq(year)
        for name in p.columns:
            row = metric(q.loc[mask], p.loc[mask, name])
            results.append({"year": year, "policy": name, "full_common_rows": int(mask.sum()), **row})
    out = pd.DataFrame(results)
    expected = {(2023, "PRAMV_V1"): (89,54), (2024, "PRAMV_V1"): (86,52), (2025, "PRAMV_V1"): (82,52)}
    for (year, name), vals in expected.items():
        g = out[(out.year == year) & (out.policy == name)].iloc[0]
        assert (int(g.n), int(g.correct)) == vals, "PRAMV_SOURCE_RECONSTRUCTION_FAIL"
    out.to_csv(OUT, index=False)
    print(out[["year","policy","n","correct","accuracy","BA","up_recall","down_recall"]].to_string(index=False))
    print("Saved:", OUT)

if __name__ == "__main__":
    main()
