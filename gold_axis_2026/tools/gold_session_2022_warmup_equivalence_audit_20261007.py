import json
from pathlib import Path
import numpy as np
import pandas as pd

AX=Path(__file__).resolve().parents[1]
OUT=AX/"SESSION_2022_WARMUP_EQUIV_OUT";OUT.mkdir(exist_ok=True)
OLD=AX/"GOLD_SESSION_TARGETS_V5_EQUIVALENT_WARMUP_2022.csv"
W=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2022.csv"
S=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2022.csv"
OX=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
NX=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_OVERLAP.csv"
KEY=["label_date","partition","window"]

def b(s):
    return s.astype(str).str.lower().eq("true")

def main():
    a=pd.read_csv(OLD); z=pd.concat([pd.read_csv(W),pd.read_csv(S)],ignore_index=True)
    if a.duplicated(KEY).any() or z.duplicated(KEY).any():raise RuntimeError("DUP_KEYS")
    cols=KEY+["start_utc","end_utc","start_price","end_price","return","direction","final_trainable"]
    a=a[cols].copy();z=z[cols].copy()
    for q in (a,z):
        q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
        q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
        q["final_trainable"]=b(q.final_trainable)
    m=a.merge(z,on=KEY,how="outer",suffixes=("_old","_new"),indicator=True,validate="one_to_one")
    both=m[m._merge.eq("both")].copy()
    mism={}
    for c in ["start_utc","end_utc","direction","final_trainable"]:
        ok=both[f"{c}_old"].fillna("NA").astype(str).eq(both[f"{c}_new"].fillna("NA").astype(str))
        mism[c]=int((~ok).sum())
    for c,tol in [("start_price",1e-9),("end_price",1e-9),("return",1e-12)]:
        x=pd.to_numeric(both[f"{c}_old"],errors="coerce").to_numpy(float)
        y=pd.to_numeric(both[f"{c}_new"],errors="coerce").to_numpy(float)
        ok=(np.isnan(x)&np.isnan(y))|np.isclose(x,y,rtol=0,atol=tol)
        mism[c]=int((~ok).sum())
    f_old=set(map(tuple,a[a.final_trainable][KEY].astype(str).to_numpy()))
    f_new=set(map(tuple,z[z.final_trainable][KEY].astype(str).to_numpy()))

    ox=pd.read_csv(OX,usecols=["dt_utc","open","high","low","close"])
    nx=pd.read_csv(NX,usecols=["dt_utc","open","high","low","close"])
    for q in (ox,nx):q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True)
    r=ox.merge(nx,on="dt_utc",suffixes=("_old","_new"),validate="one_to_one")
    raw={}
    for c in ["open","high","low","close"]:
        raw[c]=int((pd.to_numeric(r[f"{c}_old"])-pd.to_numeric(r[f"{c}_new"])).abs().gt(0).sum())

    passed=(int((m._merge!="both").sum())==0 and all(v==0 for v in mism.values())
            and f_old==f_new and len(r)>0 and all(v==0 for v in raw.values()))
    out={"status":"PASS" if passed else "FAIL","target_rows_old":len(a),"target_rows_new":len(z),
         "matched_keys":int((m._merge=="both").sum()),"old_only":int((m._merge=="left_only").sum()),
         "new_only":int((m._merge=="right_only").sum()),"target_field_mismatches":mism,
         "final_trainable_old":len(f_old),"final_trainable_new":len(f_new),
         "final_trainable_key_sets_equal":f_old==f_new,"raw_common_rows":len(r),
         "raw_ohlc_mismatches":raw}
    (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
    if not passed:raise RuntimeError("EQUIVALENCE_FAIL")

if __name__=="__main__":main()
