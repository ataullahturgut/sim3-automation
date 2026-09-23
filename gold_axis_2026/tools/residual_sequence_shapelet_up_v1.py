from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

IDENTITY="RESIDUAL_SEQUENCE_SHAPELET_UP_V1_RESEARCH"
LENGTHS=(13,25,49)
STEP=6
Z90=1.2815515655446004


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


def wilson(k,n):
    if n<=0:return None
    p=k/n; z=Z90
    den=1+z*z/n
    center=p+z*z/(2*n)
    rad=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)
    return (center-rad)/den


def nearest_rank(v,q):
    x=sorted(float(z) for z in v)
    if not x:return None
    k=max(1,min(len(x),int(math.ceil(q*len(x)))))
    return x[k-1]


def seq_from_rets(rets):
    r=np.asarray(rets,float)
    if len(r)<239: raise RuntimeError(f"SHORT_PATH:{len(r)}")
    rv=float(np.sum(r*r))
    if rv<=0 or not math.isfinite(rv): raise RuntimeError("BAD_RV")
    p=np.concatenate(([0.0],np.cumsum(r)))/math.sqrt(rv)
    if len(p)<97: raise RuntimeError("TERMINAL_PATH_TOO_SHORT")
    s=p[-97:].copy()
    s-=s[0]
    return s


def zvec(x):
    x=np.asarray(x,float)
    sd=float(np.std(x,ddof=0))
    if sd<1e-8:return None
    return (x-float(np.mean(x)))/sd


def norm_windows(seq,L):
    w=np.lib.stride_tricks.sliding_window_view(np.asarray(seq,float),L)
    mu=np.mean(w,axis=1,keepdims=True)
    sd=np.std(w,axis=1,ddof=0,keepdims=True)
    ok=(sd[:,0]>=1e-8)
    if not np.any(ok): return np.empty((0,L),float)
    return (w[ok]-mu[ok])/sd[ok]


def candidate_starts(L):
    last=97-L
    starts=list(range(0,last+1,STEP))
    if starts[-1]!=last: starts.append(last)
    return starts


def build_candidates(train):
    by_len={}
    for L in LENGTHS:
        arr=[]; meta=[]
        for row in train:
            s=row["seq"]
            for st in candidate_starts(L):
                z=zvec(s[st:st+L])
                if z is None: continue
                arr.append(z)
                meta.append({
                    "source_origin_date":row["origin_date"],
                    "source_target_date":row["target_date"],
                    "length":L,
                    "start":st,
                })
        if not arr: raise RuntimeError(f"NO_CANDIDATES:{L}")
        by_len[L]=(np.vstack(arr),meta)
    return by_len


def dist_matrix(candidates,rows,L):
    # candidates: C x L, rows -> return C x N minimum RMS z-normalized distance
    C=candidates.shape[0]; N=len(rows)
    out=np.empty((C,N),float)
    for j,row in enumerate(rows):
        w=norm_windows(row["seq"],L)
        if len(w)==0: raise RuntimeError(f"NO_VALID_WINDOWS:{row['origin_date']}:{L}")
        # z-normalized vectors have squared norm L.
        maxdot=np.max(candidates @ w.T,axis=1)
        d2=np.maximum(0.0,2.0*L-2.0*maxdot)/L
        out[:,j]=np.sqrt(d2)
    return out


def cliffs_row(d,labels):
    up=d[labels==1]; dn=d[labels==0]
    gt=lt=0
    for x in up:
        for y in dn:
            if x>y:gt+=1
            elif x<y:lt+=1
    return (gt-lt)/(len(up)*len(dn))


def select_shapelets(train):
    labels=np.asarray([r["actual_up"] for r in train],int)
    allrows=[]
    caches={}
    candidates=build_candidates(train)
    for L,(cand,meta) in candidates.items():
        dm=dist_matrix(cand,train,L)
        caches[L]=(cand,meta,dm)
        for i,m in enumerate(meta):
            d=dm[i]
            delta=cliffs_row(d,labels)
            up=d[labels==1]; dn=d[labels==0]
            md=float(np.median(up)-np.median(dn))
            allrows.append({
                **m,"candidate_index":i,"delta":float(delta),
                "median_diff":md,
            })
    neg=[r for r in allrows if r["delta"]<0]
    pos=[r for r in allrows if r["delta"]>0]
    if not neg or not pos: raise RuntimeError("MISSING_SIGNED_SHAPELET")
    neg.sort(key=lambda r:(r["delta"],-abs(r["median_diff"]),r["length"],r["source_target_date"],r["start"]))
    pos.sort(key=lambda r:(-r["delta"],-abs(r["median_diff"]),r["length"],r["source_target_date"],r["start"]))
    upsel=neg[0]
    downsel=pos[0]
    if all(upsel[k]==downsel[k] for k in ("length","source_target_date","start")):
        downsel=pos[1]
    for sel in (upsel,downsel):
        cand,meta,dm=caches[sel["length"]]
        sel["shapelet"]=[float(x) for x in cand[sel["candidate_index"]]]
    return upsel,downsel,len(allrows)


def dist_one(seq,sel):
    L=sel["length"]
    w=norm_windows(seq,L)
    if len(w)==0: raise RuntimeError("NO_FINITE_SHAPELET_DISTANCE")
    sh=np.asarray(sel["shapelet"],float)
    maxdot=float(np.max(w @ sh))
    d2=max(0.0,2.0*L-2.0*maxdot)/L
    return math.sqrt(d2)


def attach_dist(rows,upsel,downsel):
    out=[]
    for r in rows:
        z=dict(r)
        z["d_up_shapelet"]=dist_one(r["seq"],upsel)
        z["d_down_shapelet"]=dist_one(r["seq"],downsel)
        out.append(z)
    return out


def fit(train):
    X=np.asarray([[r["d_up_shapelet"],r["d_down_shapelet"]] for r in train],float)
    y=np.asarray([r["actual_up"] for r in train],int)
    mu=X.mean(axis=0); sd=X.std(axis=0,ddof=0); sd=np.where(sd<1e-12,1.0,sd)
    m=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",class_weight=None,max_iter=5000)
    m.fit((X-mu)/sd,y)
    return m,mu,sd


def probs(model,mu,sd,rows):
    X=np.asarray([[r["d_up_shapelet"],r["d_down_shapelet"]] for r in rows],float)
    return model.predict_proba((X-mu)/sd)[:,1]


def auc(y,p):
    y=np.asarray(y,int)
    if len(np.unique(y))<2:return None
    return float(roc_auc_score(y,p))


def score(rows,model,mu,sd,tau):
    p=probs(model,mu,sd,rows)
    out=[]
    for r,v in zip(rows,p):
        z=dict(r); z["p_up"]=float(v); z["tau"]=tau; z["shapelet_call"]=int(v>tau); out.append(z)
    return out


def metrics(rows):
    y=np.asarray([r["actual_up"] for r in rows],int)
    p=np.asarray([r["shapelet_call"] for r in rows],int)
    pr=np.asarray([r["p_up"] for r in rows],float)
    tp=int(np.sum((p==1)&(y==1))); fp=int(np.sum((p==1)&(y==0)))
    fn=int(np.sum((p==0)&(y==1))); tn=int(np.sum((p==0)&(y==0)))
    calls=tp+fp; au=tp+fn; ad=fp+tn
    return {
        "n":len(rows),"actual_up":au,"actual_down":ad,"calls":calls,
        "true_up":tp,"false_up":fp,"missed_up":fn,"true_down_abstain":tn,
        "precision":tp/calls if calls else None,
        "recall":tp/au if au else None,
        "false_up_fpr":fp/ad if ad else None,
        "coverage":calls/len(rows) if rows else None,
        "wilson90_lcb_precision":wilson(tp,calls),
        "auc":auc(y,pr),
        "brier":float(np.mean((pr-y)**2)) if len(y) else None,
    }


def corr(a,b):
    if len(a)<2:return None
    x=np.asarray(a,float); y=np.asarray(b,float)
    if np.std(x)<1e-15 or np.std(y)<1e-15:return 1.0 if np.allclose(x,y) else 0.0
    return float(np.corrcoef(x,y)[0,1])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--pre-ledger",type=Path,required=True)
    ap.add_argument("--baseline-result",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority",a.route_module)
    base=load_mod("base_authority",a.base_module)
    cbr=load_mod("cbr_authority",a.cbr_code)
    sqrt_mod=route.load_sqrt_mod(a.sqrt_code)

    spine=route.load_external_spine(a.external_spine)
    raw=route.build_external_5m(a.raw_root)
    ext_audit=route.external_reconstruction_audit(raw,spine)
    if not ext_audit["passed"]: raise RuntimeError("EXTERNAL_RECON_FAIL")
    daily=route.load_external_daily_for_sqrt(spine)
    sq,sqsum=route.external_sqrt_cases(sqrt_mod,daily)
    rr,rrsum=route.external_router_rows(base,spine)
    residual,routesum=route.route_external_sqrt_cases(sq,rr)

    ext=[]
    for r in residual:
        z={"evaluation_year":int(r["evaluation_year"]),"origin_date":r["origin_date"],"target_date":r["target_date"],"actual_up":int(r["actual_up"]),"seq":seq_from_rets(raw[r["origin_date"]]["rets"])}
        ext.append(z)
    train=[r for r in ext if r["evaluation_year"]==2020]
    cal=[r for r in ext if r["evaluation_year"]==2021]
    if len(train)!=72 or sum(r["actual_up"] for r in train)!=35: raise RuntimeError("TRAIN2020_COUNT_FAIL")
    if len(cal)!=26 or sum(r["actual_up"] for r in cal)!=11: raise RuntimeError("CAL2021_COUNT_FAIL")

    upsel,downsel,ncand=select_shapelets(train)
    train2=attach_dist(train,upsel,downsel)
    cal2=attach_dist(cal,upsel,downsel)
    model,mu,sd=fit(train2)
    cal_probs=probs(model,mu,sd,cal2)
    down_scores=[float(p) for p,r in zip(cal_probs,cal2) if r["actual_up"]==0]
    if len(down_scores)<10: raise RuntimeError("CAL_DOWN_SUPPORT_FAIL")
    q80=nearest_rank(down_scores,.80); tau=max(.50,float(q80))
    cal_scored=score(cal2,model,mu,sd,tau)

    gov_raw=cbr.load_paths(["2020-01-02","2025-12-31"])

    # Source transfer for selected shapelet distances.
    eu=[]; ed=[]; gu=[]; gd=[]
    common=[]
    for d in sorted(set(raw)&set(gov_raw)):
        if len(raw[d]["rets"])<239 or len(gov_raw[d])<239: continue
        es=seq_from_rets(raw[d]["rets"]); gs=seq_from_rets(gov_raw[d])
        eu.append(dist_one(es,upsel)); ed.append(dist_one(es,downsel))
        gu.append(dist_one(gs,upsel)); gd.append(dist_one(gs,downsel)); common.append(d)
    transfer={
        "overlap_n":len(common),
        "up_distance":{"pearson":corr(eu,gu),"median_abs_diff":float(np.median(np.abs(np.asarray(eu)-np.asarray(gu))))},
        "down_distance":{"pearson":corr(ed,gd),"median_abs_diff":float(np.median(np.abs(np.asarray(ed)-np.asarray(gd))))},
    }
    transfer["passed"]=bool(
        len(common)>=300 and transfer["up_distance"]["pearson"]>=.90 and transfer["down_distance"]["pearson"]>=.90
        and transfer["up_distance"]["median_abs_diff"]<=.10 and transfer["down_distance"]["median_abs_diff"]<=.10
    )
    if not transfer["passed"]:
        result={"identity":IDENTITY,"status":"BLOCKED_SOURCE_OR_ROUTE_INTEGRITY","integrity_errors":["SHAPELET_DISTANCE_TRANSFER_FAIL"],"source_transfer":transfer}
        (a.out/"GOLD_CONTROL_RESIDUAL_SEQUENCE_SHAPELET_UP_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2)); return 2

    pre=route.load_pre_unresolved(a.pre_ledger)
    pre_rows=[]
    for r in pre:
        od=r["origin_date"]
        if od not in gov_raw: raise RuntimeError(f"GOV_PATH_MISSING:{od}")
        pre_rows.append({"evaluation_year":int(r["evaluation_year"]),"origin_date":od,"target_date":r["target_date"],"actual_up":int(r["actual_up"]),"seq":seq_from_rets(gov_raw[od])})
    if len(pre_rows)!=26 or sum(r["actual_up"] for r in pre_rows)!=13: raise RuntimeError("PRE_COUNT_FAIL")

    stress=route.reconstruct_2025(base,a.sqrt_parent)
    y25=[]
    for r in stress:
        od=r["origin_date"]
        y25.append({"evaluation_year":2025,"origin_date":od,"target_date":r["target_date"],"actual_up":int(r["actual_up"]),"seq":seq_from_rets(gov_raw[od])})
    if len(y25)!=74 or sum(r["actual_up"] for r in y25)!=35: raise RuntimeError("Y25_COUNT_FAIL")

    pre2=attach_dist(pre_rows,upsel,downsel); y252=attach_dist(y25,upsel,downsel)
    pre_scored=score(pre2,model,mu,sd,tau); y25_scored=score(y252,model,mu,sd,tau)

    byyear={str(y):metrics([r for r in pre_scored if r["evaluation_year"]==y]) for y in (2022,2023,2024)}
    pooled=metrics(pre_scored); m25=metrics(y25_scored); mcal=metrics(cal_scored)

    supportive=bool(
        pooled["n"]==26 and pooled["calls"]>=4 and pooled["precision"] is not None and pooled["precision"]>.50
        and pooled["wilson90_lcb_precision"] is not None and pooled["wilson90_lcb_precision"]>.50
        and pooled["false_up_fpr"] is not None and pooled["false_up_fpr"]<=.25
    )
    t25=bool(
        m25["calls"]>=5 and m25["precision"] is not None and m25["precision"]>(35/74)
        and m25["false_up_fpr"] is not None and m25["false_up_fpr"]<.50
    )
    if supportive and t25: status="SHAPELET_UP_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT"
    elif supportive: status="PRE2025_SHAPELET_UP_SIGNAL_ONLY"
    else: status="SHAPELET_UP_V1_NOT_SUPPORTED"

    baseline=json.loads(a.baseline_result.read_text(encoding="utf-8"))
    result={
        "identity":IDENTITY,"date":"2026-09-23","status":status,"integrity_errors":[],
        "design":{"discovery_train_year":2020,"calibration_year":2021,"governed_eval":[2022,2023,2024],"locked_transport":2025,
                  "terminal_returns":96,"shapelet_lengths_points":list(LENGTHS),"candidate_start_step_points":STEP,
                  "n_candidates":ncand,"model":"L2 LogisticRegression C=1.0 on two selected shapelet distances",
                  "tau":"max(0.50, q80 of 2021 realized-DOWN pUP)"},
        "external_reconstruction":ext_audit,"external_sqrt_summary":sqsum,"external_router_summary":rrsum,"external_route_summary":routesum,
        "selected_up_shapelet":upsel,"selected_down_shapelet":downsel,
        "model":{"mu":[float(x) for x in mu],"sd":[float(x) for x in sd],"coef":[float(x) for x in model.coef_[0]],"intercept":float(model.intercept_[0])},
        "calibration_2021":{"tau":tau,"q80_down_pup":q80,**mcal},
        "source_transfer":transfer,
        "by_year_2022_2024":byyear,"pooled_2022_2024":pooled,"pre2025_supportive":supportive,
        "locked_2025":{**m25,"transport_supportive":t25,"residual_up_base_rate":35/74},
        "comparison_to_one_sided_up2_v1":{
            "shapelet_pre2025":{"calls":pooled["calls"],"precision":pooled["precision"],"recall":pooled["recall"],"fpr":pooled["false_up_fpr"],"auc":pooled["auc"]},
            "one_sided_logit_pre2025":{"calls":baseline["pooled_2022_2024"]["up2_calls"],"precision":baseline["pooled_2022_2024"]["up_precision"],"recall":baseline["pooled_2022_2024"]["missed_up_recall"],"fpr":baseline["pooled_2022_2024"]["false_up_fpr"],"auc":baseline["pooled_2022_2024"]["auc"]},
            "descriptive_only":True
        },
        "governance":{"random_split":False,"2025_tuning":False,"2026_used":False,"automatic_ensemble":False,"runtime_promotion":False}
    }
    (a.out/"GOLD_CONTROL_RESIDUAL_SEQUENCE_SHAPELET_UP_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    ledger=cal_scored+pre_scored+y25_scored
    fields=["evaluation_year","origin_date","target_date","actual_up","d_up_shapelet","d_down_shapelet","p_up","tau","shapelet_call"]
    with (a.out/"GOLD_CONTROL_RESIDUAL_SEQUENCE_SHAPELET_UP_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in ledger:w.writerow({k:r.get(k,"") for k in fields})

    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
