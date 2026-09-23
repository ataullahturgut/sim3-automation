from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

FEATURES = [
    "sqrt_score",
    "lag1_close_return",
    "direct_up_fraction",
    "legacy_up_fraction",
    "downside_share",
    "intraday_end_norm",
    "close_location",
    "last_quarter_return_norm",
    "max_drawdown_norm",
    "trough_position",
    "recovery_to_close_ratio",
    "post_trough_return_norm",
    "post_trough_positive_fraction",
]

CONTRASTS = {
    "CAPTURED_UP_vs_MISSED_UP": ("CAPTURED_UP","MISSED_UP"),
    "REJECTED_DOWN_vs_FALSE_UP_ACTUAL_DOWN": ("REJECTED_DOWN","FALSE_UP_ACTUAL_DOWN"),
    "MISSED_UP_vs_REJECTED_DOWN": ("MISSED_UP","REJECTED_DOWN"),
    "CAPTURED_UP_vs_REJECTED_DOWN": ("CAPTURED_UP","REJECTED_DOWN"),
}

EXPECTED_PRE = {
    "CAPTURED_UP":8,
    "MISSED_UP":5,
    "FALSE_UP_ACTUAL_DOWN":3,
    "REJECTED_DOWN":10,
}
EXPECTED_2025 = {
    "CAPTURED_UP":13,
    "MISSED_UP":22,
    "FALSE_UP_ACTUAL_DOWN":12,
    "REJECTED_DOWN":27,
}


def read_csv(path: Path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def quantile(xs,q):
    x=sorted(float(v) for v in xs)
    if not x:
        return None
    p=(len(x)-1)*q
    lo=math.floor(p); hi=math.ceil(p)
    if lo==hi:
        return x[lo]
    return x[lo]+(x[hi]-x[lo])*(p-lo)


def stats(xs):
    x=[float(v) for v in xs]
    if not x:
        return {"n":0,"mean":None,"median":None,"q25":None,"q75":None,"iqr":None}
    q25=quantile(x,.25); q75=quantile(x,.75)
    return {
        "n":len(x),
        "mean":sum(x)/len(x),
        "median":quantile(x,.5),
        "q25":q25,
        "q75":q75,
        "iqr":q75-q25,
    }


def cliffs_delta(a,b):
    aa=[float(x) for x in a]; bb=[float(x) for x in b]
    if not aa or not bb:
        return None
    gt=lt=0
    for x in aa:
        for y in bb:
            if x>y: gt+=1
            elif x<y: lt+=1
    return (gt-lt)/(len(aa)*len(bb))


def exact_perm_median_p(a,b):
    aa=[float(x) for x in a]; bb=[float(x) for x in b]
    n1=len(aa); combined=aa+bb
    if n1==0 or len(bb)==0:
        return None
    obs=abs(quantile(aa,.5)-quantile(bb,.5))
    total=0; extreme=0
    idx=range(len(combined))
    for comb in itertools.combinations(idx,n1):
        s=set(comb)
        x=[combined[i] for i in idx if i in s]
        y=[combined[i] for i in idx if i not in s]
        d=abs(quantile(x,.5)-quantile(y,.5))
        total+=1
        if d+1e-15>=obs:
            extreme+=1
    return extreme/total


def bh_adjust(pvals):
    items=[(i,p) for i,p in enumerate(pvals) if p is not None]
    m=len(items)
    out=[None]*len(pvals)
    ranked=sorted(items,key=lambda z:z[1])
    prev=1.0
    tmp=[None]*m
    for rank in range(m,0,-1):
        i,p=ranked[rank-1]
        q=min(prev,p*m/rank)
        prev=q
        tmp[rank-1]=(i,q)
    for i,q in tmp:
        out[i]=q
    return out


def group_name(actual_up,call):
    if actual_up==1 and call==1: return "CAPTURED_UP"
    if actual_up==1 and call==0: return "MISSED_UP"
    if actual_up==0 and call==1: return "FALSE_UP_ACTUAL_DOWN"
    return "REJECTED_DOWN"


def build_join(up2,morph,parent):
    mmap={(r["origin_date"],r["target_date"]):r for r in morph}
    pmap={(r["origin_date"],r["target_date"]):r for r in parent}
    rows=[]; errs=[]
    for u in up2:
        key=(u["origin_date"],u["target_date"])
        m=mmap.get(key); p=pmap.get(key)
        if m is None:
            errs.append(f"MORPH_MISSING:{key}"); continue
        if p is None:
            errs.append(f"PARENT_MISSING:{key}"); continue
        if int(u["actual_up"])!=int(m["actual_up"]):
            errs.append(f"LABEL_MISMATCH:{key}")
        actual=int(u["actual_up"]); call=int(u["up2_call"])
        logret=float(p["target_close_return"])
        if actual!=int(logret>0):
            errs.append(f"PARENT_LABEL_MISMATCH:{key}")
        row={
            "evaluation_year":int(u["evaluation_year"]),
            "origin_date":u["origin_date"],
            "target_date":u["target_date"],
            "actual_up":actual,
            "up2_call":call,
            "group":group_name(actual,call),
            "p_up":float(u["p_up"]),
            "target_simple_return":math.exp(logret)-1.0,
            "target_abs_return":abs(math.exp(logret)-1.0),
        }
        for f in FEATURES:
            src = u if f in u and u[f] != "" else m
            row[f]=float(src[f])
            if not math.isfinite(row[f]):
                errs.append(f"NONFINITE:{key}:{f}")
        # exact duplicated-feature consistency where expected
        if abs(float(u["downside_share"])-float(m["downside_share"]))>1e-12:
            errs.append(f"DOWNSIDE_SHARE_MISMATCH:{key}")
        if abs(float(u["close_location"])-float(m["close_location"]))>1e-12:
            errs.append(f"CLOSE_LOCATION_MISMATCH:{key}")
        if abs(float(u["last_quarter_return_norm"])-float(m["last_quarter_return_norm"]))>1e-12:
            errs.append(f"LAST_QUARTER_MISMATCH:{key}")
        rows.append(row)
    if len(rows)!=len(up2):
        errs.append(f"JOIN_COUNT:{len(rows)}:{len(up2)}")
    return rows,errs


def counts(rows):
    d=defaultdict(int)
    for r in rows:
        d[r["group"]]+=1
    return dict(d)


def period_group_stats(rows):
    out={}
    for g in EXPECTED_PRE:
        rr=[r for r in rows if r["group"]==g]
        out[g]={
            "n":len(rr),
            "features":{f:stats([r[f] for r in rr]) for f in FEATURES},
            "diagnostic_p_up":stats([r["p_up"] for r in rr]),
            "target_simple_return":stats([r["target_simple_return"] for r in rr]),
            "target_abs_return":stats([r["target_abs_return"] for r in rr]),
        }
    return out


def contrast(rows,g1,g2,with_p):
    a=[r for r in rows if r["group"]==g1]
    b=[r for r in rows if r["group"]==g2]
    out={}
    pvals=[]
    for f in FEATURES:
        av=[r[f] for r in a]; bv=[r[f] for r in b]
        p=exact_perm_median_p(av,bv) if with_p else None
        pvals.append(p)
        out[f]={
            "delta":cliffs_delta(av,bv),
            "median_diff":quantile(av,.5)-quantile(bv,.5),
            "median_first":quantile(av,.5),
            "median_second":quantile(bv,.5),
            "exact_perm_p_median":p,
        }
    qs=bh_adjust(pvals) if with_p else [None]*len(FEATURES)
    for f,q in zip(FEATURES,qs):
        out[f]["bh_q"]=q
    # diagnostic score and outcome severity, not part of FDR family
    for f in ("p_up","target_abs_return","target_simple_return"):
        av=[r[f] for r in a]; bv=[r[f] for r in b]
        out[f]={
            "delta":cliffs_delta(av,bv),
            "median_diff":quantile(av,.5)-quantile(bv,.5),
            "median_first":quantile(av,.5),
            "median_second":quantile(bv,.5),
            "exact_perm_p_median":exact_perm_median_p(av,bv) if with_p else None,
            "bh_q":None,
        }
    return out


def stability_label(dpre,d25):
    if dpre is None or d25 is None:
        return "WEAK_OR_INCONSISTENT"
    same=(dpre==0 and d25==0) or (dpre*d25>0)
    if same and abs(dpre)>=0.474 and abs(d25)>=0.33:
        return "STRONG_STABLE"
    if same and abs(dpre)>=0.33 and abs(d25)>=0.20:
        return "MODERATE_STABLE"
    if abs(dpre)>=0.33:
        return "PRE2025_ONLY"
    return "WEAK_OR_INCONSISTENT"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--up2",type=Path,required=True)
    ap.add_argument("--morph",type=Path,required=True)
    ap.add_argument("--parent",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    rows,errs=build_join(read_csv(a.up2),read_csv(a.morph),read_csv(a.parent))
    pre=[r for r in rows if r["evaluation_year"]<=2024]
    y25=[r for r in rows if r["evaluation_year"]==2025]

    if counts(pre)!=EXPECTED_PRE:
        errs.append(f"PRE_COUNTS:{counts(pre)}")
    if counts(y25)!=EXPECTED_2025:
        errs.append(f"Y25_COUNTS:{counts(y25)}")

    pre_con={}; y25_con={}; stable={}
    for name,(g1,g2) in CONTRASTS.items():
        pre_con[name]=contrast(pre,g1,g2,True)
        y25_con[name]=contrast(y25,g1,g2,False)
        stable[name]={}
        for f in FEATURES:
            stable[name][f]={
                "label":stability_label(pre_con[name][f]["delta"],y25_con[name][f]["delta"]),
                "pre2025_delta":pre_con[name][f]["delta"],
                "locked2025_delta":y25_con[name][f]["delta"],
                "pre2025_median_diff":pre_con[name][f]["median_diff"],
                "locked2025_median_diff":y25_con[name][f]["median_diff"],
                "pre2025_bh_q":pre_con[name][f]["bh_q"],
            }

    stable_ranked={}
    order={"STRONG_STABLE":0,"MODERATE_STABLE":1,"PRE2025_ONLY":2,"WEAK_OR_INCONSISTENT":3}
    for name,vals in stable.items():
        stable_ranked[name]=sorted(
            [{"feature":f,**v} for f,v in vals.items()],
            key=lambda x:(order[x["label"]],-abs(x["pre2025_delta"]))
        )

    result={
        "identity":"DIRECTION_ERROR_ANATOMY_AUDIT_V1_RESEARCH",
        "date":"2026-09-23",
        "status":"AUDIT_COMPLETE" if not errs else "BLOCKED_INTEGRITY",
        "integrity_errors":errs,
        "semantics":{
            "CAPTURED_UP":"UP2 call and realized UP",
            "MISSED_UP":"UP2 abstain and realized UP",
            "FALSE_UP_ACTUAL_DOWN":"UP2 call but realized DOWN; missed-DOWN analogue",
            "REJECTED_DOWN":"UP2 abstain and realized DOWN; not a positive DOWN prediction",
        },
        "counts":{"pre2025":counts(pre),"locked2025":counts(y25)},
        "features":FEATURES,
        "pre2025_group_stats":period_group_stats(pre),
        "locked2025_group_stats":period_group_stats(y25),
        "pre2025_contrasts":pre_con,
        "locked2025_contrasts":y25_con,
        "cross_period_stability":stable_ranked,
        "guardrails":{
            "causal_claim":False,
            "new_model_trained":False,
            "2025_used_for_selection":False,
            "2026_used":False,
        },
    }

    outj=a.out/"GOLD_CONTROL_DIRECTION_ERROR_ANATOMY_AUDIT_V1_RESULT_2026-09-23.json"
    outj.write_text(json.dumps(result,indent=2),encoding="utf-8")

    # concise markdown with stable patterns only
    lines=[
      "# GOLD CONTROL — DIRECTION ERROR ANATOMY AUDIT V1 RESULT","",
      f"**Status:** {result['status']}","",
      "## Group counts","",
      f"Pre-2025: {json.dumps(counts(pre),sort_keys=True)}  ",
      f"Locked 2025: {json.dumps(counts(y25),sort_keys=True)}","",
      "## Cross-period effect-size stability",""
    ]
    for name in CONTRASTS:
        lines.append(f"### {name}")
        anyrow=False
        for x in stable_ranked[name]:
            if x["label"]!="WEAK_OR_INCONSISTENT":
                anyrow=True
                lines.append(
                  f"- {x['feature']}: {x['label']}; pre delta={x['pre2025_delta']:.3f}; "
                  f"2025 delta={x['locked2025_delta']:.3f}; pre median diff={x['pre2025_median_diff']:.6g}; "
                  f"2025 median diff={x['locked2025_median_diff']:.6g}; pre BH q={x['pre2025_bh_q']}"
                )
        if not anyrow:
            lines.append("- No frozen-feature pattern met the cross-period effect-size stability labels.")
        lines.append("")
    lines += [
      "Interpretation is descriptive. REJECTED_DOWN is not a validated predicted-DOWN class.",
      "No model was trained or retuned."
    ]
    (a.out/"GOLD_CONTROL_DIRECTION_ERROR_ANATOMY_AUDIT_V1_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if not errs else 2

if __name__=="__main__":
    raise SystemExit(main())
