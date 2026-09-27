from __future__ import annotations
import base64, csv, gzip, io, json, math, os
from itertools import combinations
from pathlib import Path
import numpy as np
import psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_dma_batch1_v1 as dma

DEV_START, DEV_END = "2022-04", "2024-12"
FEATURES8 = dma.FEATURES
ALPHA = 0.99
LAMBDA = 0.99
TRAIN_WINDOWS = (60,84,108,132,None)

def all_masks(indices):
    idx=list(indices); out=[]
    for r in range(len(idx)+1):
        for c in combinations(idx,r): out.append(tuple(c))
    return out

MASKS8 = all_masks(range(8))

def scaled_custom(samples,target,n_train=None):
    keys=sorted(k for k in samples if k<target)
    if n_train is not None:
        if len(keys)<n_train: raise RuntimeError(f"TRAIN_WINDOW_UNAVAILABLE target={target} have={len(keys)} need={n_train}")
        keys=keys[-n_train:]
    if len(keys)<30: raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")
    X0=np.stack([samples[k][0] for k in keys])
    Y0=np.stack([samples[k][1] for k in keys])[:,0]
    tx0=np.asarray(samples[target][0],float)
    Xw,Yw=X0[:30],Y0[:30]
    xm,xs=Xw.mean(0),Xw.std(0); ym=float(Yw.mean()); ys=float(Yw.std())
    xs=np.where(xs<1e-9,1.0,xs); ys=1.0 if ys<1e-9 else ys
    return keys,(X0-xm)/xs,(Y0-ym)/ys,(tx0-xm)/xs,ym,ys

def run_gold(samples,target,masks,alpha=ALPHA,lam=LAMBDA,n_train=None):
    keys,X,Y,tx,ym,ys=scaled_custom(samples,target,n_train)
    states=[dma.ModelState(m,1) for m in masks]; K=len(states)
    log_post=np.full(K,-math.log(K),float)
    for t in range(len(keys)):
        log_prior=alpha*log_post; log_prior-=dma.logsumexp(log_prior)
        ll=np.empty(K,float); cached=[]
        for k,st in enumerate(states):
            z,mu,var,Rs=st.forecast(X[t],lam); e=float(Y[t]-mu[0])
            ll[k]=float(-0.5*(math.log(2*math.pi*var[0])+(e*e)/var[0]))
            cached.append((z,mu,var,Rs))
        log_post=log_prior+ll; log_post-=dma.logsumexp(log_post)
        for st,c in zip(states,cached):
            st.update(c[0],np.array([Y[t]]),c[1],c[2],c[3])
    log_prior=alpha*log_post; log_prior-=dma.logsumexp(log_prior)
    w=np.exp(log_prior); w/=w.sum()
    means=np.array([st.forecast(tx,lam)[1][0] for st in states],float)
    dma_std=float(w@means); best=int(np.argmax(w)); dms_std=float(means[best])
    pip={}
    for j in range(len(samples[target][0])):
        pip[str(j)]=float(sum(w[i] for i,m in enumerate(masks) if j in m))
    return {
        "dma_ret":dma_std*ys+ym,
        "dms_ret":dms_std*ys+ym,
        "dms_mask":list(masks[best]),
        "dms_weight":float(w[best]),
        "pip":pip,
        "train_rows":len(keys),
        "effective_models":float(1.0/np.sum(w*w)),
    }

def pred_row(bundle,target,ret,model,extra=None):
    p=base.month_shift(target,-1)
    r={"target":target,"origin":p,"model":model,"pred_log_return_gold":float(ret),
       "forecast":float(bundle.core_gold[p]*math.exp(float(ret))),
       "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[p])}
    if extra:r.update(extra)
    return r

def summarize(rows):
    return {"metrics":dma.active_metrics(rows),"yearly":dma.yearly(rows),"rows":rows}

def load_core5():
    root=Path(__file__).resolve().parents[1]
    p=root/"core5_monthly.csv.gz.b64"
    raw=gzip.decompress(base64.b64decode(p.read_text().strip())).decode()
    rd=csv.DictReader(io.StringIO(raw))
    rows=list(rd)
    cols=rd.fieldnames or []
    date_col=next((c for c in cols if c.lower()=="date"),cols[0] if cols else None)
    panel={}
    for row in rows:
        s=(row.get(date_col) or "")[:7]
        if len(s)==7 and s[4]=="-":
            vals={}
            for c in cols:
                if c==date_col: continue
                try: vals[c]=float(row[c]) if row[c] not in ("",None) else math.nan
                except Exception: vals[c]=math.nan
            panel[s]=vals
    return cols,date_col,panel

def detect_col(cols,aliases):
    lc={c.lower():c for c in cols}
    for a in aliases:
        if a in lc:return lc[a]
    for c in cols:
        z=c.lower().replace("_","").replace("-","")
        if any(a.replace("_","").replace("-","") in z for a in aliases):
            return c
    return None

def macro3(panel,cols,t):
    fed=detect_col(cols,["fedfunds","fed_funds","dff","fedfund"])
    nas=detect_col(cols,["nasdaq100","nasdaq","ndx"])
    cny=detect_col(cols,["usdcny","usd_cny","cny"])
    if not all((fed,nas,cny)): raise RuntimeError(f"CORE5_REQUIRED_MACRO_COLUMNS_NOT_FOUND cols={cols} detected={(fed,nas,cny)}")
    p,pp=base.month_shift(t,-1),base.month_shift(t,-2)
    if p not in panel or pp not in panel: raise RuntimeError(f"CORE5_MACRO_MONTH_MISSING target={t} p={p} pp={pp}")
    a,b=panel[p],panel[pp]
    vals=[a[fed]-b[fed],math.log(a[nas]/b[nas]),math.log(a[cny]/b[cny])]
    if not all(math.isfinite(v) for v in vals): raise RuntimeError(f"CORE5_MACRO_NONFINITE {t} {vals}")
    return np.array(vals,float),(fed,nas,cny)

def augment_samples(samples,panel,cols):
    out={}; detected=None
    for t,(x,y) in samples.items():
        m,det=macro3(panel,cols,t); detected=det
        out[t]=(np.r_[x,m],y.copy())
    return out,detected

def pit_snapshot_coverage():
    root=Path(__file__).resolve().parents[1]
    p=root/"v149_research/data/monthly_macro_pit_snapshot_v149.csv"
    if not p.exists(): return {"status":"NOT_FOUND"}
    with p.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    ms=[r["origin_month"] for r in rows if r.get("origin_month")]
    return {"status":"FOUND","rows":len(rows),"first":min(ms) if ms else None,"last":max(ms) if ms else None,
            "covers_full_dev_from_2022_03": bool(ms and min(ms)<="2022-03")}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,DEV_END))
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in targets}

    # A. Canonical all-256 Gold-only learning curve.
    learning={}
    for n in TRAIN_WINDOWS:
        tag="MAX" if n is None else f"N{n}"
        dma_rows=[]; dms_rows=[]; dms_sizes=[]
        for t in targets:
            z=run_gold(cache[t],t,MASKS8,n_train=n)
            dma_rows.append(pred_row(bundle,t,z["dma_ret"],f"CANONICAL256_DMA_{tag}",{"train_rows":z["train_rows"]}))
            dms_rows.append(pred_row(bundle,t,z["dms_ret"],f"CANONICAL256_DMS_{tag}",{"train_rows":z["train_rows"],"dms_mask":z["dms_mask"],"dms_weight":z["dms_weight"]}))
            dms_sizes.append(len(z["dms_mask"]))
        learning[tag]={"DMA":summarize(dma_rows),"DMS":summarize(dms_rows),"avg_dms_size":float(np.mean(dms_sizes))}
    curve=[]
    for tag in ["N60","N84","N108","N132","MAX"]:
        m=learning[tag]["DMS"]["metrics"]
        curve.append({"window":tag,"sum_abs_error":m["sum_abs_error"],"mae":m["mae"],"direction_correct":m["direction_correct"],"direction_accuracy_pct":m["direction_accuracy_pct"]})
    finite=[x for x in curve if x["window"]!="MAX"]
    best_by_error=min(curve,key=lambda x:x["sum_abs_error"])
    maxrow=next(x for x in curve if x["window"]=="MAX")
    n60=next(x for x in curve if x["window"]=="N60")
    monotone_nonincreasing=all(finite[i+1]["sum_abs_error"]<=finite[i]["sum_abs_error"] for i in range(len(finite)-1)) and maxrow["sum_abs_error"]<=finite[-1]["sum_abs_error"]
    sample_diag={
        "curve":curve,
        "best_by_error":best_by_error,
        "max_vs_n60_improvement_usd":float(n60["sum_abs_error"]-maxrow["sum_abs_error"]),
        "max_vs_n60_improvement_pct":float((n60["sum_abs_error"]-maxrow["sum_abs_error"])/n60["sum_abs_error"]*100.0),
        "monotone_error_decline_with_more_history":bool(monotone_nonincreasing),
        "interpretation_rule":"Data-shortage supported only if error materially and broadly declines as history grows and MAX is best/near-best."
    }

    # B. Literature-aligned information-set diagnostic.
    # GPR is deliberately excluded: current PIT macro snapshot does not cover the full DEV history.
    cols,date_col,panel=load_core5()
    macro_results={}
    detected=None
    spaces={
        "GOLD2_ONLY":all_masks([0,1]),
        "MARKET3_ONLY":None,
        "GOLD2_PLUS_MARKET3":None,
    }
    for t in targets:
        aug,det=augment_samples(cache[t],panel,cols); detected=det
        if spaces["MARKET3_ONLY"] is None:
            spaces["MARKET3_ONLY"]=all_masks([8,9,10])
            spaces["GOLD2_PLUS_MARKET3"]=all_masks([0,1,8,9,10])
        for name,masks in spaces.items():
            samples=cache[t] if name=="GOLD2_ONLY" else aug
            z=run_gold(samples,t,masks,n_train=None)
            macro_results.setdefault(name,{"DMA":[],"DMS":[]})
            macro_results[name]["DMA"].append(pred_row(bundle,t,z["dma_ret"],f"{name}_DMA"))
            macro_results[name]["DMS"].append(pred_row(bundle,t,z["dms_ret"],f"{name}_DMS",{"dms_mask":z["dms_mask"],"dms_weight":z["dms_weight"]}))
    macro_summary={k:{meth:summarize(rows) for meth,rows in v.items()} for k,v in macro_results.items()}
    info_compare=[]
    for name in ("GOLD2_ONLY","MARKET3_ONLY","GOLD2_PLUS_MARKET3"):
        for meth in ("DMA","DMS"):
            m=macro_summary[name][meth]["metrics"]
            info_compare.append({"space":name,"method":meth,"sum_abs_error":m["sum_abs_error"],"mae":m["mae"],"direction_correct":m["direction_correct"],"direction_accuracy_pct":m["direction_accuracy_pct"]})

    after=read_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    pit=pit_snapshot_coverage()
    out={
        "scope":"DMA_CAUSE_DIAGNOSTICS_V1",
        "authority_contract_audit":{
            "binding_plan_commit":"9af2868f5390e5778f096531f32ac3f7cf5a276e",
            "binding_plan_time_utc":"2026-09-26T21:46:56Z",
            "plan_precedes_first_dma_execution":True,
            "canonical_requirement":"Gold-only, all 2^8=256 frozen predictor subsets, intercept included.",
            "prior_execution_discrepancy":"Previous runs used GOLD_MR-mandatory 128-subset authority lane and also a custom Multi4 lane. Those runs are retained as exploratory evidence but cannot substitute for canonical 256-subset authority evidence."
        },
        "literature_evidence":{
            "aye_2015":"Monthly gold DMA/DMS uses broad macro-financial factors: business cycle, nominal, interest rate, commodity, exchange rate, stock, plus stress/uncertainty.",
            "chen_yang_lan_2026":"Monthly gold IDMA identifies Nasdaq short-horizon, interest rates medium/long horizon, and lagged GPR long horizon.",
            "koop_korobilis_2012":"Forgetting factors near one imply gradual evolution and long effective memory."
        },
        "learning_curve_canonical256":learning,
        "sample_size_diagnostic":sample_diag,
        "information_set_diagnostic":{
            "evidence_class":"DIAGNOSTIC_ONLY_NOT_PRODUCTION_SELECTION",
            "why":"Tests whether literature-aligned market information adds signal; not eligible to alter frozen production feature contract.",
            "core5_columns":cols,
            "date_column":date_col,
            "detected_market_columns":{"fed":detected[0],"nasdaq":detected[1],"usdcny":detected[2]},
            "transformations":{"fed":"one-month change","nasdaq":"one-month log return","usdcny":"one-month log return"},
            "gpr_excluded":"Full-DEV origin-safe GPR coverage is not proven by the available PIT snapshot; no non-PIT GPR is used.",
            "pit_macro_snapshot":pit,
            "comparison":info_compare,
            "details":macro_summary
        },
        "source_checks":bundle.source_checks,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "database":"READ_ONLY",
        "2025_2026_used_for_selection_or_diagnostic":False,
        "random_split":"NONE"
    }
    Path("dma_cause_diagnostics_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "sample_size_diagnostic":sample_diag,
        "information_set_comparison":info_compare,
        "detected_market_columns":out["information_set_diagnostic"]["detected_market_columns"],
        "pit_macro_snapshot":pit,
        "canonical_max_dma":learning["MAX"]["DMA"]["metrics"],
        "canonical_max_dms":learning["MAX"]["DMS"]["metrics"],
        "authority_invariants_unchanged":after==bundle.invariants_before
    },sort_keys=True))

if __name__=="__main__":
    main()
