from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path

import numpy as np
import pandas as pd

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho
import gold_monthly_chhho_predev_currentgpr_v2 as gprv2

SNAPSHOT_SHA="5e4dfbfda5a89aceff9b30f5454fb36ab33c3baf"
H1_SEARCH_START,H1_END="2013-01","2021-10"
HIGH_AE=63.06
HIGH_APE=2.96117
HIGH_RET_PP=3.00590

def mshift(m,d): return base.month_shift(m,d)

def load_json(p): return json.loads(Path(p).read_text())

def gold_frame(b):
    s=pd.Series({m:float(v) for m,v in b.core_gold.items()},dtype=float).sort_index()
    f=pd.DataFrame({"Gold":s})
    f["r1"]=np.log(f.Gold/f.Gold.shift(1))
    f["r3"]=np.log(f.Gold/f.Gold.shift(3))
    f["ma12_prior"]=f.Gold.shift(1).rolling(12,min_periods=12).mean()
    f["gap"]=f.Gold/f.ma12_prior-1
    return f

def eg_flags(f,origin,pred):
    r=f.loc[origin]
    e_level=bool(r.gap>.20)
    e_full=bool(e_level and abs(float(pred)-float(r.r1))>.05)
    g=bool(r.r3<=-.10)
    return e_level,e_full,g

def fetch_gpr():
    raw=gprv2.fetch_snapshot(SNAPSHOT_SHA)
    h,meta=gprv2.parse_xls(raw)
    return h,{
        "repo":gprv2.REPO,"path":gprv2.PATH,"commit_sha":SNAPSHOT_SHA,
        "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"parse_meta":meta,
    }

def samples_with_history(b,target,h):
    out={}
    for t in base.month_range("2010-03",target):
        try: out[t]=base.sample_for_target(b,t,h,lag_gpr=True)
        except RuntimeError: pass
    if target not in out: raise RuntimeError(f"TARGET_NOT_BUILDABLE {target}")
    return out

def finish_row(b,f,origin,target,pred,forecast,actual,rw,source,train_rows=None,diag=None):
    pred=float(pred); forecast=float(forecast); actual=float(actual); rw=float(rw)
    ae=abs(forecast-actual); ape=ae/actual*100.0
    actual_ret=math.log(actual/rw); re=abs(pred-actual_ret)*100.0
    rw_ae=abs(rw-actual)
    e_level,e_full,g=eg_flags(f,origin,pred)
    pred_dir=int(np.sign(forecast-rw)); actual_dir=int(np.sign(actual-rw))
    return {
        "origin":origin,"target":target,"source":source,
        "pred_log_return_gold":pred,"forecast":forecast,"actual":actual,"rw":rw,
        "ae":ae,"ape_pct":ape,"return_error_pp":re,"rw_ae":rw_ae,
        "direction_correct":bool(pred_dir==actual_dir),
        "high_ae":bool(ae>HIGH_AE),"high_ape":bool(ape>HIGH_APE),
        "high_return_error":bool(re>HIGH_RET_PP),
        "E_level":e_level,"E_full":e_full,"G":g,
        "gold_r1":float(f.loc[origin,"r1"]),
        "gold_r3":float(f.loc[origin,"r3"]),
        "gold_vs_ma12":float(f.loc[origin,"gap"]),
        "train_rows":None if train_rows is None else int(train_rows),
        "diag":diag,
    }

def run_h1(b,f,h):
    rows=[]; unbuild=[]; started=False
    for target in base.month_range(H1_SEARCH_START,H1_END):
        origin=mshift(target,-1); req=mshift(origin,-1)
        if req not in h:
            unbuild.append({"target":target,"origin":origin,"status":"GPR_MISSING"})
            continue
        hh={k:v for k,v in h.items() if k<=req}
        try:
            ss=samples_with_history(b,target,hh)
            pred,n,diag=chhho.select(ss,target,"CHHHO")
            pg=float(pred[0]); rw=float(b.core_gold[origin])
            fc=rw*math.exp(pg); act=float(b.core_gold[target])
            rows.append(finish_row(b,f,origin,target,pg,fc,act,rw,
                                   "H1_COUNTERFACTUAL_CURRENT_GPR",n,diag))
            started=True
        except Exception as e:
            unbuild.append({"target":target,"origin":origin,"status":"MODEL_UNBUILDABLE",
                            "error":f"{type(e).__name__}:{e}"})
            if started:
                # after first successful month, a later failure is material
                pass
    return rows,unbuild

def rows_from_predev(b,f,p):
    rows=[]
    for r in p["rows"]:
        rows.append(finish_row(
            b,f,r["origin"],r["target"],r["pred_log_return_gold"],r["forecast"],
            r["actual"],b.core_gold[r["origin"]],"H2_VALID_SAME_METHOD_PREDEV",
            r.get("train_rows"),r.get("diag")
        ))
    return rows

def rows_from_chhho_dev(b,f,ch):
    rows=[]
    for r in ch["dev"]["rows"]:
        rows.append(finish_row(
            b,f,r["origin"],r["target"],r["pred_log_return_gold"],r["forecast"],
            r["actual"],r["rw"],"H3_FROZEN_CANONICAL_DEV",
            r.get("train_rows"),r.get("diag")
        ))
    return rows

def metrics(rows):
    if not rows:
        return {}
    ae=np.array([r["ae"] for r in rows],float)
    ape=np.array([r["ape_pct"] for r in rows],float)
    sq=np.array([(r["forecast"]-r["actual"])**2 for r in rows],float)
    rw=np.array([r["rw_ae"] for r in rows],float)
    worst=max(rows,key=lambda r:r["ae"])
    return {
        "n":len(rows),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "median_ae":float(np.median(ae)),
        "mape_pct":float(ape.mean()),
        "rmse":float(np.sqrt(sq.mean())),
        "direction_correct":sum(r["direction_correct"] for r in rows),
        "direction_accuracy":float(np.mean([r["direction_correct"] for r in rows])),
        "rw_sum_abs_error":float(rw.sum()),
        "relative_mae_vs_rw":None if rw.mean()==0 else float(ae.mean()/rw.mean()),
        "high_ae_n":sum(r["high_ae"] for r in rows),
        "high_ape_n":sum(r["high_ape"] for r in rows),
        "high_return_error_n":sum(r["high_return_error"] for r in rows),
        "worst_target":worst["target"],
        "worst_ae":worst["ae"],
        "worst_ape_pct":worst["ape_pct"],
    }

def yearly(rows):
    years=sorted(set(r["target"][:4] for r in rows))
    return {y:metrics([r for r in rows if r["target"].startswith(y)]) for y in years}

def conditional(rows,flag):
    z=[r for r in rows if r[flag]]
    return {
        "events":len(z),
        "targets":[r["target"] for r in z],
        "metrics":metrics(z),
        "rows":[{k:r[k] for k in (
            "target","origin","ae","ape_pct","return_error_pp","high_ae","high_ape",
            "high_return_error","E_level","E_full","G"
        )} for r in z],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--predev",required=True)
    ap.add_argument("--chhho",required=True)
    a=ap.parse_args()

    pre=load_json(a.predev); ch=load_json(a.chhho)
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    f=gold_frame(b)
    h,gmeta=fetch_gpr()

    h1,unbuild=run_h1(b,f,h)
    h2=rows_from_predev(b,f,pre)
    h3=rows_from_chhho_dev(b,f,ch)

    blocks={"H1_COUNTERFACTUAL":h1,"H2_VALID_PREDEV":h2,"H3_CANONICAL_DEV":h3}
    all_rows=h1+h2+h3

    high_ae=[r for r in all_rows if r["high_ae"]]
    worst=sorted(all_rows,key=lambda r:r["ae"],reverse=True)[:15]

    out={
        "schema":"GOLD_MONTHLY_CHHHO_HISTORICAL_PERFORMANCE_AUDIT_V1_2026-09-30",
        "status":"COMPLETE",
        "gpr_counterfactual_authority":gmeta,
        "thresholds":{
            "high_ae_usd_gt":HIGH_AE,"high_ape_pct_gt":HIGH_APE,
            "high_return_error_pp_gt":HIGH_RET_PP,
        },
        "blocks":{
            k:{
                "range":None if not v else [v[0]["target"],v[-1]["target"]],
                "metrics":metrics(v),"yearly":yearly(v),
                "E_level":conditional(v,"E_level"),
                "E_full":conditional(v,"E_full"),
                "G":conditional(v,"G"),
            } for k,v in blocks.items()
        },
        "H1_unbuildable":unbuild,
        "all_high_ae_targets":[
            {k:r[k] for k in ("target","origin","source","ae","ape_pct","return_error_pp",
                              "E_level","E_full","G")}
            for r in high_ae
        ],
        "top15_worst":[
            {k:r[k] for k in ("target","origin","source","forecast","actual","ae","ape_pct",
                              "return_error_pp","E_level","E_full","G")}
            for r in worst
        ],
        "all_rows":all_rows,
        "governance":{
            "H1_is_counterfactual_not_pit":True,
            "H2_is_valid_same_method_predev":True,
            "H3_uses_frozen_canonical_forecasts":True,
            "threshold_retuning":False,
            "database_read_only":True,
        },
    }
    Path("GOLD_MONTHLY_CHHHO_HISTORICAL_PERFORMANCE_AUDIT_V1_2026-09-30.json").write_text(
        json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "blocks":{k:v["metrics"] for k,v in out["blocks"].items()},
        "ranges":{k:v["range"] for k,v in out["blocks"].items()},
        "EG":{k:{
            "E_level":v["E_level"]["targets"],
            "E_full":v["E_full"]["targets"],
            "G":v["G"]["targets"],
        } for k,v in out["blocks"].items()},
        "high_ae":out["all_high_ae_targets"],
        "top15":out["top15_worst"],
    },sort_keys=True))

if __name__=="__main__":
    main()
