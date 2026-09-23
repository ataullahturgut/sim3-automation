from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

IDENTITY="DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH"
FEATURES=[
    "late_rv_share",
    "late_downside_rv_share",
    "late_downside_intensity",
    "terminal_negative_run_frac",
    "max_negative_run_frac",
    "new_low_rate_last_quarter",
    "time_near_low_last_quarter",
    "post_trough_efficiency",
    "post_trough_positive_move_share",
    "post_trough_sign_change_rate",
    "recovery_speed_norm",
    "near_trough_revisit_rate",
    "last_hour_return_norm",
    "last_hour_slope_norm",
    "last_hour_trend_r2",
    "late_acceleration_norm",
    "max_negative_shock_share",
    "top3_negative_shock_share",
]
CONTRASTS={
    "CAPTURED_UP_vs_MISSED_UP":("CAPTURED_UP","MISSED_UP"),
    "CAPTURED_UP_vs_FALSE_UP_ACTUAL_DOWN":("CAPTURED_UP","FALSE_UP_ACTUAL_DOWN"),
    "MISSED_UP_vs_REJECTED_DOWN":("MISSED_UP","REJECTED_DOWN"),
}
EXPECTED_PRE={"CAPTURED_UP":8,"MISSED_UP":5,"FALSE_UP_ACTUAL_DOWN":3,"REJECTED_DOWN":10}
EXPECTED_2025={"CAPTURED_UP":13,"MISSED_UP":22,"FALSE_UP_ACTUAL_DOWN":12,"REJECTED_DOWN":27}


def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_FAIL:{name}:{path}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def read_csv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group_name(actual,call):
    if actual==1 and call==1: return "CAPTURED_UP"
    if actual==1 and call==0: return "MISSED_UP"
    if actual==0 and call==1: return "FALSE_UP_ACTUAL_DOWN"
    return "REJECTED_DOWN"


def qtile(x,q):
    a=sorted(float(v) for v in x)
    if not a: return None
    p=(len(a)-1)*q
    lo=int(math.floor(p)); hi=int(math.ceil(p))
    if lo==hi: return a[lo]
    return a[lo]+(a[hi]-a[lo])*(p-lo)


def stat(x):
    a=[float(v) for v in x]
    if not a: return {"n":0,"mean":None,"median":None,"q25":None,"q75":None,"iqr":None}
    q25=qtile(a,.25); q75=qtile(a,.75)
    return {"n":len(a),"mean":sum(a)/len(a),"median":qtile(a,.5),"q25":q25,"q75":q75,"iqr":q75-q25}


def cliffs(a,b):
    aa=[float(v) for v in a]; bb=[float(v) for v in b]
    gt=lt=0
    for x in aa:
        for y in bb:
            if x>y: gt+=1
            elif x<y: lt+=1
    return (gt-lt)/(len(aa)*len(bb))


def perm_p_median(a,b):
    aa=[float(v) for v in a]; bb=[float(v) for v in b]
    n1=len(aa); z=aa+bb
    obs=abs(qtile(aa,.5)-qtile(bb,.5))
    total=extreme=0
    idx=range(len(z))
    for comb in itertools.combinations(idx,n1):
        s=set(comb)
        x=[z[i] for i in idx if i in s]
        y=[z[i] for i in idx if i not in s]
        d=abs(qtile(x,.5)-qtile(y,.5))
        total+=1
        if d+1e-15>=obs: extreme+=1
    return extreme/total


def bh(pvals):
    m=len(pvals)
    order=sorted(range(m),key=lambda i:pvals[i])
    out=[None]*m
    prev=1.0
    for rank in range(m,0,-1):
        i=order[rank-1]
        v=min(prev,pvals[i]*m/rank)
        prev=v; out[i]=v
    return out


def max_neg_run(r):
    best=cur=0
    for v in r:
        if v<0:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return best


def terminal_neg_run(r):
    n=0
    for v in r[::-1]:
        if v<0: n+=1
        else: break
    return n


def sign_change_rate(r):
    s=[1 if v>0 else -1 for v in r if abs(v)>0]
    if len(s)<2: return 0.0
    return sum(s[i]!=s[i-1] for i in range(1,len(s)))/(len(s)-1)


def ols_slope_r2(y):
    yy=np.asarray(y,float)
    x=np.arange(len(yy),dtype=float)
    if len(yy)<2: return 0.0,0.0
    xm=x.mean(); ym=yy.mean()
    den=float(np.sum((x-xm)**2))
    slope=float(np.sum((x-xm)*(yy-ym))/den) if den>0 else 0.0
    fit=ym+slope*(x-xm)
    ss_tot=float(np.sum((yy-ym)**2))
    ss_res=float(np.sum((yy-fit)**2))
    r2=0.0 if ss_tot<=1e-30 else max(0.0,min(1.0,1.0-ss_res/ss_tot))
    return slope,r2


def features(rets):
    r=np.asarray(rets,float)
    N=len(r)
    if N<239: raise RuntimeError(f"SHORT_DAY:{N}")
    rv=float(np.sum(r*r))
    if rv<=0: raise RuntimeError("ZERO_RV")
    scale=math.sqrt(rv)
    neg_sq=np.where(r<0,r*r,0.0)
    drv=float(np.sum(neg_sq))
    path=np.concatenate(([0.0],np.cumsum(r)))
    pmin=float(np.min(path)); pmax=float(np.max(path)); span=max(pmax-pmin,1e-15)
    trough_idx=int(np.argmin(path))
    trough=float(path[trough_idx]); close=float(path[-1])

    qn=max(1,int(math.ceil(.25*N)))
    qr=r[-qn:]
    q_neg_sq=np.where(qr<0,qr*qr,0.0)
    qrv=float(np.sum(qr*qr)); qdrv=float(np.sum(q_neg_sq))

    # Return endpoints belonging to final quarter.
    start_endpoint=N-qn+1
    running_min=np.minimum.accumulate(path)
    new_lows=0
    for idx in range(start_endpoint,N+1):
        prevmin=float(np.min(path[:idx]))
        if float(path[idx]) < prevmin-1e-15:
            new_lows+=1
    near_low_threshold=pmin+0.2*span
    near_low=sum(float(path[idx])<=near_low_threshold for idx in range(start_endpoint,N+1))/qn

    post=r[trough_idx:] if trough_idx<N else np.asarray([],float)
    post_path=path[trough_idx+1:] if trough_idx<N else np.asarray([],float)
    if len(post)==0:
        post_eff=0.0; post_pos_share=0.0; post_scr=0.0; rec_speed=0.0; revisit=1.0
    else:
        total_abs=float(np.sum(np.abs(post)))
        recovery=close-trough
        post_eff=recovery/total_abs if total_abs>0 else 0.0
        post_pos=float(np.sum(np.where(post>0,post,0.0)))
        post_pos_share=post_pos/total_abs if total_abs>0 else 0.0
        post_scr=sign_change_rate(post)
        frac=len(post)/N
        rec_speed=(recovery/scale)/frac if frac>0 else 0.0
        revisit=float(np.mean(post_path <= (trough+0.2*span))) if len(post_path) else 1.0

    Hn=min(12,N)
    hr=r[-Hn:]
    hp=np.concatenate(([0.0],np.cumsum(hr)))
    slope,r2=ols_slope_r2(hp)
    hret=float(np.sum(hr))/scale
    hslope=slope*N/scale
    half=Hn//2
    if half>0:
        first=float(np.sum(hr[:half]))
        second=float(np.sum(hr[half:]))
        accel=(second-first)/scale
    else:
        accel=0.0

    neg_values=np.sort(neg_sq[neg_sq>0])[::-1]
    max_shock=float(neg_values[0]/drv) if drv>0 and len(neg_values) else 0.0
    top3=float(np.sum(neg_values[:3])/drv) if drv>0 and len(neg_values) else 0.0

    out={
        "late_rv_share":qrv/rv,
        "late_downside_rv_share":qdrv/drv if drv>0 else 0.0,
        "late_downside_intensity":qdrv/rv,
        "terminal_negative_run_frac":terminal_neg_run(r)/N,
        "max_negative_run_frac":max_neg_run(r)/N,
        "new_low_rate_last_quarter":new_lows/qn,
        "time_near_low_last_quarter":near_low,
        "post_trough_efficiency":post_eff,
        "post_trough_positive_move_share":post_pos_share,
        "post_trough_sign_change_rate":post_scr,
        "recovery_speed_norm":rec_speed,
        "near_trough_revisit_rate":revisit,
        "last_hour_return_norm":hret,
        "last_hour_slope_norm":hslope,
        "last_hour_trend_r2":r2,
        "late_acceleration_norm":accel,
        "max_negative_shock_share":max_shock,
        "top3_negative_shock_share":top3,
    }
    for k,v in out.items():
        if not math.isfinite(float(v)):
            raise RuntimeError(f"NONFINITE:{k}:{v}")
    return out


def counts(rows):
    out={k:0 for k in EXPECTED_PRE}
    for r in rows: out[r["group"]]+=1
    return out


def period_stats(rows):
    out={}
    for g in EXPECTED_PRE:
        rr=[r for r in rows if r["group"]==g]
        out[g]={"n":len(rr),"features":{f:stat([r[f] for r in rr]) for f in FEATURES}}
    return out


def contrast(rows,g1,g2,with_p):
    a=[r for r in rows if r["group"]==g1]
    b=[r for r in rows if r["group"]==g2]
    out={}; ps=[]
    for f in FEATURES:
        av=[r[f] for r in a]; bv=[r[f] for r in b]
        p=perm_p_median(av,bv) if with_p else None
        ps.append(p)
        out[f]={
            "delta":cliffs(av,bv),
            "median_first":qtile(av,.5),
            "median_second":qtile(bv,.5),
            "median_diff":qtile(av,.5)-qtile(bv,.5),
            "exact_perm_p_median":p,
        }
    if with_p:
        qs=bh(ps)
        for f,q in zip(FEATURES,qs): out[f]["bh_q"]=q
    else:
        for f in FEATURES: out[f]["bh_q"]=None
    return out


def label(dp,d25):
    same=(dp==0 and d25==0) or dp*d25>0
    if same and abs(dp)>=.474 and abs(d25)>=.33: return "STRONG_STABLE"
    if same and abs(dp)>=.33 and abs(d25)>=.20: return "MODERATE_STABLE"
    if abs(dp)>=.33: return "PRE2025_ONLY"
    return "WEAK_OR_INCONSISTENT"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--up2",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    cbr=load_mod("cbr_authority",a.cbr_code)
    paths=cbr.load_paths(["2022-01-01","2025-12-31"])
    ledger=read_csv(a.up2)

    errs=[]; rows=[]
    for r in ledger:
        y=int(r["evaluation_year"])
        if y not in (2022,2023,2024,2025): continue
        d=r["origin_date"]
        if d not in paths:
            errs.append(f"PATH_MISSING:{d}"); continue
        actual=int(r["actual_up"]); call=int(r["up2_call"])
        z={
            "evaluation_year":y,
            "origin_date":d,
            "target_date":r["target_date"],
            "group":group_name(actual,call),
            **features(paths[d]),
        }
        rows.append(z)

    pre=[r for r in rows if r["evaluation_year"]<=2024]
    y25=[r for r in rows if r["evaluation_year"]==2025]
    if counts(pre)!=EXPECTED_PRE: errs.append(f"PRE_COUNTS:{counts(pre)}")
    if counts(y25)!=EXPECTED_2025: errs.append(f"Y25_COUNTS:{counts(y25)}")
    if len(rows)!=100: errs.append(f"ROW_COUNT:{len(rows)}")

    pre_con={}; y25_con={}; stability={}
    for name,(g1,g2) in CONTRASTS.items():
        pre_con[name]=contrast(pre,g1,g2,True)
        y25_con[name]=contrast(y25,g1,g2,False)
        arr=[]
        for f in FEATURES:
            dp=pre_con[name][f]["delta"]; d25=y25_con[name][f]["delta"]
            arr.append({
                "feature":f,
                "label":label(dp,d25),
                "pre2025_delta":dp,
                "locked2025_delta":d25,
                "pre2025_median_diff":pre_con[name][f]["median_diff"],
                "locked2025_median_diff":y25_con[name][f]["median_diff"],
                "pre2025_bh_q":pre_con[name][f]["bh_q"],
            })
        rank={"STRONG_STABLE":0,"MODERATE_STABLE":1,"PRE2025_ONLY":2,"WEAK_OR_INCONSISTENT":3}
        arr.sort(key=lambda x:(rank[x["label"]],-abs(x["pre2025_delta"])))
        stability[name]=arr

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":"AUDIT_COMPLETE" if not errs else "BLOCKED_INTEGRITY",
        "integrity_errors":errs,
        "counts":{"pre2025":counts(pre),"locked2025":counts(y25)},
        "features":FEATURES,
        "pre2025_group_stats":period_stats(pre),
        "locked2025_group_stats":period_stats(y25),
        "pre2025_contrasts":pre_con,
        "locked2025_contrasts":y25_con,
        "cross_period_stability":stability,
        "guardrails":{
            "new_predictive_model_trained":False,
            "random_split":False,
            "2025_used_for_design_or_tuning":False,
            "2026_used":False,
            "production_writes":False,
        }
    }
    (a.out/"GOLD_CONTROL_DIRECTION_MECHANISM_GAP_AUDIT_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    lines=[
      "# GOLD CONTROL — DIRECTION MECHANISM-GAP AUDIT V1 RESULT","",
      f"**Status:** `{result['status']}`","",
      f"Pre-2025 counts: `{json.dumps(counts(pre),sort_keys=True)}`  ",
      f"Locked-2025 counts: `{json.dumps(counts(y25),sort_keys=True)}`",""
    ]
    for name in CONTRASTS:
        lines.append(f"## {name}")
        useful=[x for x in stability[name] if x["label"]!="WEAK_OR_INCONSISTENT"]
        if not useful:
            lines.append("- No frozen path-dynamic feature met the cross-period stability rule.")
        for x in useful:
            lines.append(
                f"- **{x['feature']}** — {x['label']}; pre delta={x['pre2025_delta']:.3f}, "
                f"2025 delta={x['locked2025_delta']:.3f}, pre median diff={x['pre2025_median_diff']:.6g}, "
                f"2025 median diff={x['locked2025_median_diff']:.6g}, pre BH q={x['pre2025_bh_q']}"
            )
        lines.append("")
    lines += [
      "No classifier was trained. Stable patterns may motivate a separately preregistered future model only."
    ]
    (a.out/"GOLD_CONTROL_DIRECTION_MECHANISM_GAP_AUDIT_V1_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if not errs else 2

if __name__=="__main__":
    raise SystemExit(main())
