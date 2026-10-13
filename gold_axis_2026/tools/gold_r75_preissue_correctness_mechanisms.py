#!/usr/bin/env python3
"""R75 preregistered R67 origin-safe correctness-gate diagnostics, 2026-10-13.
Run with: python gold_axis_2026/tools/gold_r75_preissue_correctness_mechanisms.py
No external libraries; no new fitting / no target-window features as predictors.
"""
from __future__ import annotations
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "GOLD_R67_20261012_H3_AS_DAY_AND_OVN_CONDITIONER_2023_2026_ROWS.csv"
PREFIX = ROOT / "GOLD_R75_20261013_PREISSUE_CORRECT_ERROR_"
YEARS = (2023, 2024, 2025, 2026)
GATES = ("FULL", "CONF_HALF", "CONF_Q75", "H3_AGREE", "PRIOR_DAY_ALIGN",
         "PRIOR_OVN_ALIGN", "PRIOR_DAY_REVERSE", "CALM_PRIOR_OVN",
         "CONF_HALF_AND_H3_AGREE")


def quantile(xs, p):
    z = sorted(xs)
    j = (len(z) - 1) * p
    a = int(j)
    return z[a] + (z[min(a + 1, len(z) - 1)] - z[a]) * (j - a)


def auc_rank(z):  # Correct = positive, preissue confidence = score
    pos = [q["margin"] for q in z if q["correct"] == 1]
    neg = [q["margin"] for q in z if q["correct"] == 0]
    if not pos or not neg:
        return None
    return sum(1 if a > b else (.5 if a == b else 0) for a in pos for b in neg) / (len(pos) * len(neg))


def mean(xs):
    return sum(xs)/len(xs) if xs else None


def median(xs):
    return quantile(xs, .5) if xs else None


def load():
    with SRC.open() as f:
        data = list(csv.DictReader(f))
    out = []
    for x in data:
        if int(x["year"]) not in YEARS:
            continue
        y = int(x["y"]); pred = int(x["new_pred"])
        r = {"clock":x["clock"], "day":x["day"], "year":int(x["year"]),
             "y":y, "pred":pred, "h3bit":int(x["h3bit"]), "prob":float(x["prob"]),
             "prior_day":float(x["prior_day"]),
             "prior_overnight":float(x["prior_overnight"]), "ret":float(x["ret"])}
        r["margin"] = abs(r["prob"] - .5)
        r["correct"] = int(y == pred)
        r["h3correct"] = int(y == r["h3bit"])
        out.append(r)
    out.sort(key=lambda d:(d["clock"], d["day"]))
    return out


def gate(g, r, t):
    m = r["margin"]
    if g == "FULL": return True
    if g == "CONF_HALF": return m >= t["conf_half"]
    if g == "CONF_Q75": return m >= t["conf_q75"]
    if g == "H3_AGREE": return r["pred"] == r["h3bit"]
    sig = 1 if r["pred"] else -1
    if g == "PRIOR_DAY_ALIGN": return r["prior_day"] * sig > 0
    if g == "PRIOR_OVN_ALIGN": return r["prior_overnight"] * sig > 0
    if g == "PRIOR_DAY_REVERSE": return r["prior_day"] * sig < 0
    if g == "CALM_PRIOR_OVN": return abs(r["prior_overnight"]) <= t["calm_ovn"]
    if g == "CONF_HALF_AND_H3_AGREE":
        return m >= t["conf_half"] and r["pred"] == r["h3bit"]
    raise ValueError(g)


def metrics(z, full_n, dev_class):
    n = len(z)
    up = sum(v["y"] for v in z)
    p_up = sum(v["pred"] for v in z)
    tp = sum(v["pred"] == 1 and v["y"] == 1 for v in z)
    tn = sum(v["pred"] == 0 and v["y"] == 0 for v in z)
    up_rec = tp / up if up else None
    dn_rec = tn / (n-up) if n-up else None
    return {
        "n":n, "coverage": n/full_n if full_n else None, "correct":tp+tn,
        "acc":(tp+tn)/n if n else None,
        "ba":(up_rec+dn_rec)/2 if up_rec is not None and dn_rec is not None else None,
        "up_recall":up_rec,"down_recall":dn_rec,
        "actual_UP":up, "pred_UP":p_up,
        "h3_correct":sum(v["h3correct"] for v in z),
        "always_UP_correct":up,"always_DOWN_correct":n-up,
        "frozen_DEV_class_correct":sum(v["y"]==dev_class for v in z),
        "mean_abs_ret":mean([abs(v["ret"]) for v in z]),
        "near_zero_lt25bp":sum(abs(v["ret"]) < .0025 for v in z),
        "large_ge50bp_n":sum(abs(v["ret"]) >= .005 for v in z),
        "large_ge50bp_correct":sum(abs(v["ret"]) >= .005 and v["correct"] for v in z),
        "large_ge100bp_n":sum(abs(v["ret"]) >= .01 for v in z),
        "large_ge100bp_correct":sum(abs(v["ret"]) >= .01 and v["correct"] for v in z)
    }


def block_ci_vs_dev_majority(z, dev_class, repeats=2500, block=5):
    # Same-row paired correct-minus-frozen-DEV-baseline, blocks within 2025 & 2026.
    rng = random.Random(75013)
    byyear = [sorted([v for v in z if v["year"]==y], key=lambda v:v["day"])
              for y in (2025, 2026)]
    if min(map(len, byyear)) < block:
        return [None, None]
    draws = []
    for _ in range(repeats):
        diffs = []
        for ys in byyear:
            m = len(ys)
            sample = []
            while len(sample)<m:
                start = rng.randrange(m-block+1)
                sample.extend(ys[start:start+block])
            diffs.extend(v["correct"] - int(v["y"]==dev_class) for v in sample[:m])
        draws.append(sum(diffs)/len(diffs))
    return [quantile(draws,.025),quantile(draws,.975)]


def main():
    data = load()
    allm = []
    results = {"input":str(SRC.relative_to(ROOT)),
               "method":"Locked DEV-feature thresholds; open periods 2025/2026 retrospective only",
               "clocks":{}, "prereg_gates":list(GATES)}
    for clock in ("DAY", "OVN"):
        byclock = [r for r in data if r["clock"] == clock]
        dev = [r for r in byclock if r["year"] in (2023,2024)]
        threshold = {"conf_half":quantile([r["margin"] for r in dev],.5),
                     "conf_q75":quantile([r["margin"] for r in dev],.75),
                     "calm_ovn":quantile([abs(r["prior_overnight"]) for r in dev],.5)}
        dev_majority = int(sum(r["y"] for r in dev) >= len(dev)/2)
        clock_res = {"thresholds":threshold, "frozen_DEV_majority_UP":bool(dev_majority),
                     "annual_feature_diagnostics":{}, "gates":{}}
        for yr in YEARS:
            z = [r for r in byclock if r["year"] == yr]
            c = [r for r in z if r["correct"]]
            w = [r for r in z if not r["correct"]]
            clock_res["annual_feature_diagnostics"][str(yr)] = {
                "n":len(z), "median_abs_prior_day":median([abs(r["prior_day"]) for r in z]),
                "median_abs_prior_overnight":median([abs(r["prior_overnight"]) for r in z]),
                "median_abs_future_ret_DIAGNOSTIC_ONLY":median([abs(r["ret"]) for r in z]),
                "confidence_auc_predicts_correct":auc_rank(z),
                "median_confidence_if_correct":median([r["margin"] for r in c]),
                "median_confidence_if_wrong":median([r["margin"] for r in w]),
            }
        for g in GATES:
            z=[r for r in byclock if gate(g,r,threshold)]
            blocks = {}
            for yr in YEARS:
                zyr=[r for r in z if r["year"]==yr]
                total=sum(r["year"]==yr for r in byclock)
                m=metrics(zyr,total,dev_majority)
                blocks[str(yr)]=m
                allm.append(dict(clock=clock,gate=g,year=yr,**m))
            opened = [r for r in z if r["year"] >= 2025]
            ci = block_ci_vs_dev_majority(opened, dev_majority)
            # No post-hoc gate selection; criteria are diagnostic screens only.
            dev_ok = all(blocks[str(y)]["n"]>=25 and
                blocks[str(y)]["acc"] > metrics([r for r in byclock if r["year"]==y],
                                              sum(r["year"]==y for r in byclock),dev_majority)["acc"]
                and blocks[str(y)]["correct"] > max(blocks[str(y)]["always_UP_correct"],
                                                    blocks[str(y)]["always_DOWN_correct"])
                for y in (2023,2024))
            trans_ok= all(blocks[str(y)]["n"]>=25
                    and blocks[str(y)]["acc"] > metrics([r for r in byclock if r["year"]==y],
                        sum(r["year"]==y for r in byclock),dev_majority)["acc"]
                    and blocks[str(y)]["acc"] > (blocks[str(y)]["frozen_DEV_class_correct"]/
                        blocks[str(y)]["n"] +.05) for y in (2025,2026))
            clock_res["gates"][g]={"by_year":blocks,
                "opened_paired_gain_ci_95_vs_frozen_DEV_majority":ci,
                "prereg_DEV_screen":dev_ok, "prereg_opened_screen":trans_ok,
                "promote":bool(dev_ok and trans_ok and ci[0] is not None and ci[0]>0)}
        results["clocks"][clock]=clock_res

    with (Path(str(PREFIX)+"SUMMARY.json")).open("w") as f:
        json.dump(results, f,indent=2,ensure_ascii=False)
    cols=list(allm[0])
    with (Path(str(PREFIX)+"GATE_METRICS.csv")).open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(allm)
    lines=["# R75 — Original R67 DAY/OVN success/failure gate audit",
           "", "## Verdict", "PREDECLARED GATE: none qualifies all-year corroboration.",
           "R67 targets strictly post-decision; no native H3 label-space accuracy.",
           "2025/2026 previously opened; no live bank fills/firstprints. 2023 HistData incomplete.",
           ""]
    for clock in ("DAY","OVN"):
        v=results["clocks"][clock]
        lines.extend([f"## {clock} (locked DEV thresholds: {v['thresholds']})", "",
                      "|Pre-origin gate|2023|2024|2025 opened|2026 opened|Qualifies?|",
                      "|---|---:|---:|---:|---:|---|"])
        for g in GATES:
            d=v["gates"][g]
            score=lambda y:f"{d['by_year'][str(y)]['correct']}/{d['by_year'][str(y)]['n']} ({100*d['by_year'][str(y)]['acc']:.1f}%)" if d['by_year'][str(y)]['n'] else "-"
            lines.append("|"+g+"|"+"|".join(score(y) for y in YEARS)+"|"+("YES" if d["promote"] else "NO")+"|")
        lines.extend(["", "### Feature stability",
                      "|year|confidence AUROC for correctness|median prior OVN |ret| %|median next-window |ret| % OUTCOME ONLY|",
                      "|---|---:|---:|---:|"])
        for y in YEARS:
            p=v["annual_feature_diagnostics"][str(y)]
            lines.append(f"|{y}|{p['confidence_auc_predicts_correct']:.3f}|{100*p['median_abs_prior_overnight']:.3f}|{100*p['median_abs_future_ret_DIAGNOSTIC_ONLY']:.3f}|")
        lines.append("")
    lines.extend(["## Caveats", "Retrospective reference signal and underpowered 2023 HistData; historical H3 issue time/provider first-print partly unknown.",
                  "Confidence, agreement, and prior returns are origin-available only CONDITIONAL on model timestamps and upstream publication readiness.",
                  "Daily small moves are outcome-only diagnostics, not predecision gating. No retrospective choose-best-gate optimization and no user-bank spread P&L.",
                  "A confidence AUC below 0.5 in 2026 indicates worsening reliability, not that inverse trades are proven profitable.",
                  "2023/2024 are DEV, not final untouched holdout; 2025/2026 repeated retrospective inspections.",
                  ""])
    Path(str(PREFIX)+"RESULT.md").write_text("\n".join(lines))
    print(json.dumps({clock:{"n":{str(y):next(x for x in results['clocks'][clock]['gates']['FULL']['by_year'].items() if x[0]==str(y))[1]['n'] for y in YEARS},
                             "passed":[g for g,v in results['clocks'][clock]['gates'].items() if v['promote']]}
                      for clock in ("DAY","OVN")},indent=2))


if __name__=="__main__": main()
