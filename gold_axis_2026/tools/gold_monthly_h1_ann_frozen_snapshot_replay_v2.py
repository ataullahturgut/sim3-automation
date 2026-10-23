"""Immutable-origin data snapshot and leak-controlled replays of frozen ANN FULL7/REDUCED4.

No original ANN solver code changes. All seven components read identical bytes
for all 54 origins. Database accessed only by 'snapshot' action, never by
component runners. Research only, StakTrakr price firstprints unverified.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import gold_monthly_h1_retrain_v2 as source

CONTRACT="NEON_STAKTRAKR_GPR_V2"
COMPONENTS=("VANILLA","MPA","SCA","DE_ABC","ADAPTIVE_TLBO","TLBO_TUNED_PSO","MPA_SCA")
START,END="2022-04","2026-09"

def serialized(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(serialized(obj)).hexdigest()

def source_snapshot(output):
    if not os.getenv("NEON_DATABASE_URL"):
        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")
    os.environ["GOLD_MONTHLY_H1_DATA_CONTRACT"]=CONTRACT
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    source.source_gate(b)
    records=[]
    for t in base.month_range(START,END):
        orig=base.month_shift(t,-1)
        samples=source.features_for_target(b,t)
        proof=source.input_audit(b,t,samples)
        last=sorted(k for k in samples if k<t)
        if not last or last[-1]!=orig or len(last)<140:
            raise RuntimeError("BAD_TRAINING_CUTOFF_"+t)
        # Use the same origin GPR vintage throughout the completed training
        # sample set; no post-origin history or target-month Y in predictor.
        features={}
        for m in sorted(samples):
            x,y=samples[m]
            if m>t or (m<t and m>orig): raise RuntimeError("FUTURE_SAMPLE_LEAK")
            if x.shape!=(8,) or not np.isfinite(x).all(): raise RuntimeError("BAD_FEATURES")
            if m==t:
                features[m]=[x.astype(float).tolist(),None]
            else:
                if y.shape!=(4,) or not np.isfinite(y).all():raise RuntimeError("BAD_TRAINING_Y")
                features[m]=[x.astype(float).tolist(),y.astype(float).tolist()]
        if features[t][1] is not None:raise RuntimeError("TARGET_LABEL_PRESENT")
        rec={
            "target_month":t,"origin_month":orig,
            "origin_gold_average":float(b.core_gold[orig]),
            "actual_xau_average":float(b.core_gold[t]),
            "origin_feature_sha256":proof["input_sha256"],
            "gpr_source_commit_sha":proof["gpr_commit_sha"],
            "gpr_source_file":proof["gpr_file"],
            "training_first":last[0],"training_last":last[-1],
            "training_rows":len(last),
            "samples":features,
        }
        rec["model_input_sha256"]=sha({k:rec[k] for k in ("target_month","origin_month","samples","origin_feature_sha256","gpr_source_commit_sha")})
        records.append(rec)
        print("ANN_SINGLE_VINTAGE_SNAPSHOT",t,rec["training_rows"],
              rec["model_input_sha256"][:12],flush=True)
    if len(records)!=54:raise RuntimeError("INVALID_SNAPSHOT_MONTHS")
    payload={
       "kind":"GOLD_H1_CANONICAL_ANN_SOURCE_SNAPSHOT",
       "data_source":CONTRACT,
       "model_input_firstprint_certified":False,
       "target_y_replaced_with_null":True,
       "models":["FULL7_ANN","REDUCED4_ANN"],
       "model_component_list":list(COMPONENTS),
       "records":records,
    }
    payload["snapshot_sha256"]=sha({k:v for k,v in payload.items() if k!="snapshot_sha256"})
    Path(output).write_text(json.dumps(payload,indent=None,separators=(",",":"),allow_nan=False)+"\n")
    print("ANN_CANONICAL_SNAPSHOT_PASS",len(records),payload["snapshot_sha256"],flush=True)

def read_snapshot(path):
    p=json.loads(Path(path).read_text())
    assert p["kind"]=="GOLD_H1_CANONICAL_ANN_SOURCE_SNAPSHOT"
    assert p["data_source"]==CONTRACT
    assert p["target_y_replaced_with_null"] is True
    assert len(p["records"])==54
    assert p["snapshot_sha256"]==sha({k:v for k,v in p.items() if k!="snapshot_sha256"})
    for r in p["records"]:
        assert r["model_input_sha256"]==sha({k:r[k] for k in ("target_month","origin_month","samples","origin_feature_sha256","gpr_source_commit_sha")})
        assert r["samples"][r["target_month"]][1] is None
        assert r["training_last"]==r["origin_month"]
        assert r["training_rows"]==len(r["samples"])-1
    return p

def component_replay(inp,out,component):
    if component not in COMPONENTS: raise RuntimeError("UNKNOWN_COMPONENT")
    source_input=read_snapshot(inp)
    import gold_monthly_2026_aug_sep_topmodels_v1 as archived
    rows=[]
    for r in source_input["records"]:
        target=r["target_month"]
        samples={}
        for t,(x,y) in r["samples"].items():
            samples[t]=(np.asarray(x,dtype=float),None if y is None else np.asarray(y,dtype=float))
        assert all(t<=r["origin_month"] for t in samples if t!=target)
        assert samples[target][1] is None
        p,meta=archived.pred_component(samples,target,component)
        p=np.asarray(p,float)
        if p.shape!=(4,) or not np.isfinite(p).all() or abs(float(p[0]))>=1.0:
            raise RuntimeError("ANN_PATHOLOGICAL_PREDICTION_"+component+"_"+target)
        if int(meta["train_rows"])!=r["training_rows"]:
            raise RuntimeError("TRAINING_COUNT_MISMATCH")
        # Confirm training data arrays and target features were not overwritten
        for t,(x,y) in r["samples"].items():
            new=samples[t]
            if not np.array_equal(new[0],np.asarray(x,dtype=float)):
                raise RuntimeError("SOURCE_FEATURE_MUTATED")
            if y is None and new[1] is not None:
                raise RuntimeError("TARGET_Y_EXPOSED")
            if y is not None and not np.array_equal(new[1],np.asarray(y,dtype=float)):
                raise RuntimeError("SOURCE_Y_MUTATED")
        forecast=float(r["origin_gold_average"]*math.exp(float(p[0])))
        if not math.isfinite(forecast) or forecast<=0:raise RuntimeError("BAD_PRICE")
        rows.append({
            "target_month":target,
            "component":component,
            "snapshot_sha256":source_input["snapshot_sha256"],
            "model_input_sha256":r["model_input_sha256"],
            "origin_feature_sha256":r["origin_feature_sha256"],
            "gpr_source_commit_sha":r["gpr_source_commit_sha"],
            "training_rows":r["training_rows"],
            "training_first":r["training_first"],
            "training_last":r["training_last"],
            "forecast_xau_average":forecast,
            "actual_xau_average":r["actual_xau_average"],
            "origin_gold_average":r["origin_gold_average"],
            "prediction_gold_log_return":float(p[0]),
            "source_mutation_detected":False,
            "target_label_visible":False,
            "optimizer_details":meta,
        })
        print("ANN_FROZEN_REPLAY_SNAPSHOT",component,target,
              format(forecast,".6f"),"train=",r["training_rows"],flush=True)
    payload={
        "status":"FROZEN_COMPONENT_54_PASS",
        "source_contract":CONTRACT,
        "database_access":"NONE",
        "component":component,
        "original_model_code_changed":False,
        "snapshot_sha256":source_input["snapshot_sha256"],
        "rows":rows,
    }
    Path(out).write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("ANN_FROZEN_COMPONENT_54_PASS",component,len(rows),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("snapshot","component"))
    p.add_argument("--component",choices=COMPONENTS)
    p.add_argument("--snapshot")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    if a.mode=="snapshot":source_snapshot(a.output)
    else:
        if not a.component or not a.snapshot:raise RuntimeError("MISSING_COMPONENT_OR_SNAPSHOT")
        component_replay(a.snapshot,a.output,a.component)

if __name__=="__main__":main()
