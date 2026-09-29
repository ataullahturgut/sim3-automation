from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_rbfnn_stage1_v1 as rbfnn

def merge_bundle(dev_snapshot,current_bundle):
    b,meta=snap.load_snapshot(dev_snapshot)
    cur=json.loads(Path(current_bundle).read_text())
    # merge daily extension
    dd={m:{k:list(v) for k,v in b.daily_month_values[m].items()} for m in base.METALS}
    for r in cur["daily_extension_rows"]:
        mk=r["date"][:7]
        for m in base.METALS:
            dd[m].setdefault(mk,[]).append(float(r[m]))
    daily={m:{k:np.asarray(v,float) for k,v in q.items()} for m,q in dd.items()}
    monthly={m:{k:float(v.mean()) for k,v in daily[m].items()} for m in base.METALS}
    core=dict(b.core_gold)
    core.update({k:float(v) for k,v in cur["world_bank"]["gold_monthly"].items()})
    gpr=dict(b.gpr_vintages)
    gpr.update({o:{k:float(v) for k,v in h.items()} for o,h in cur["gpr_vintages"].items()})
    checks=dict(b.source_checks)
    checks.update({
      "public_extension_last":cur["daily_extension_last"],
      "public_extension_rows":len(cur["daily_extension_rows"]),
      "world_bank_last":cur["world_bank"]["last"],
      "neon_reads":0,
    })
    return base.DataBundle(core_gold=core,core_gpr={},daily_month_values=daily,monthly_metal=monthly,
                           gpr_vintages=gpr,source_checks=checks,invariants_before=b.invariants_before),cur,meta

def forward_x(bundle,target,gpr_history):
    p=base.month_shift(target,-1);pp=base.month_shift(target,-2)
    z=base.gpr_norm(gpr_history,pp)
    x=[]
    for metal in base.METALS:
        M=bundle.monthly_metal[metal]
        if p not in M or pp not in M: raise RuntimeError(f"FORWARD_FEATURE_MONTH_MISSING {metal} {target}")
        x.extend((math.log(M[p]/M[pp]),base.weighted_daily_return(bundle,metal,p,z)))
    return np.asarray(x,float)

def forward_samples(bundle,target,train_end):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages: raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin];out={}
    for t in base.month_range("2010-03",train_end):
        try:out[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError:continue
    tx=forward_x(bundle,target,gh)
    out[target]=(tx,np.zeros(4,float))
    return out

def predict(model,samples,target):
    if model=="CHHHO":
        p,n,diag=anfis.select(samples,target,"CHHHO")
        return np.asarray(p,float),{"train_rows":n,**diag}
    if model=="DE_ABC":
        p,diag=rbfnn.predict(samples,target,"DE_ABC")
        return np.asarray(p,float),diag
    raise KeyError(model)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dev-snapshot",required=True)
    ap.add_argument("--current-bundle",required=True)
    ap.add_argument("--model",required=True,choices=["CHHHO","DE_ABC"])
    ap.add_argument("--target",required=True,choices=["2026-09","2026-10"])
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    b,cur,meta=merge_bundle(a.dev_snapshot,a.current_bundle)
    if a.target=="2026-09":
        train_end="2026-08";role="FINAL_ORIGIN_2026_08"
    else:
        # September is incomplete at the current 2026-09-29 cutoff; do not use partial Sep as training Y.
        train_end="2026-08";role="PROVISIONAL_NOWCAST_ORIGIN_PARTIAL_2026_09"
    samples=forward_samples(b,a.target,train_end)
    p,diag=predict(a.model,samples,a.target)
    origin=base.month_shift(a.target,-1)
    if a.target=="2026-09":
        if origin not in b.core_gold: raise RuntimeError(f"WORLD_BANK_ORIGIN_MISSING {origin}")
        origin_price=float(b.core_gold[origin]);price_role="WORLD_BANK_MONTHLY_GOLD_FINAL"
        finalizable=True
    else:
        v=b.daily_month_values["Gold"].get(origin)
        if v is None or len(v)<10: raise RuntimeError("SEPTEMBER_PARTIAL_GOLD_INSUFFICIENT")
        origin_price=float(np.mean(v));price_role="STAKTRAKR_PARTIAL_MONTH_AVERAGE_PROXY"
        finalizable=False
    forecast=float(origin_price*math.exp(float(p[0])))
    out={
      "schema":"GOLD_MONTHLY_PUBLIC_FORWARD_TOP2_V1_2026-09-29",
      "model":a.model,"target":a.target,"origin":origin,"role":role,
      "train_end":train_end,"train_target_month_partial_used":False,
      "pred_log_return_gold":float(p[0]),"origin_price":origin_price,
      "origin_price_role":price_role,"forecast":forecast,
      "final_month_end_forecast":finalizable,
      "daily_data_last":cur["daily_extension_last"],
      "world_bank_last":cur["world_bank"]["last"],
      "gpr_vintage_origin":origin,
      "gpr_meta":cur["gpr_meta"][origin],
      "neon_reads":0,
      "dev_snapshot_payload_sha256":meta["payload_sha256"],
      "diag":diag,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("FORWARD_OUTPUT_GATE=PASS")
    print(json.dumps({k:out[k] for k in ["model","target","role","pred_log_return_gold","origin_price","origin_price_role","forecast","final_month_end_forecast","daily_data_last"]},sort_keys=True))
if __name__=="__main__":main()
