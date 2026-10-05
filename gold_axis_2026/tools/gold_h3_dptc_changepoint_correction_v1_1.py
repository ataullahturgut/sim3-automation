from __future__ import annotations

import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
F=AX/"GOLD_H3_DPTC_COMPETENCE_MECHANISM_FEATURES_V1_2026-10-05.csv"
OUTJ=AX/"GOLD_H3_DPTC_CHANGEPOINT_CORRECTION_V1_1_2026-10-05.json"
OUTM=AX/"GOLD_H3_DPTC_CHANGEPOINT_CORRECTION_V1_1_2026-10-05.md"
RNG=np.random.default_rng(26010051)

SHIFT=["spd_shift","energy_shift","tail_shift","te_shift","leadlag_shift","eig1_share"]
STATE=["corr_gc_nq","corr_gc_zn","corr_gc_cl","corr_gc_si","eig1_share","r_gn","r_gv"]

def robust_scale(pre,cols):
    x=pre[cols].apply(pd.to_numeric,errors="coerce").to_numpy(float)
    med=np.nanmedian(x,axis=0)
    mad=np.nanmedian(np.abs(x-med),axis=0)*1.4826
    sd=np.nanstd(x,axis=0)
    sc=np.where((mad>1e-9)&np.isfinite(mad),mad,np.where(sd>1e-9,sd,1.0))
    return med,sc

def cp(df,cols,med,sc,minseg=25,nboot=1000,block=10):
    q=df.copy()
    x=q[cols].apply(pd.to_numeric,errors="coerce").to_numpy(float)
    z=np.nan_to_num((x-med)/sc,nan=0.0,posinf=0.0,neginf=0.0)
    def best(arr):
        n=len(arr);bv=-1;bk=None
        for k in range(minseg,n-minseg):
            d=arr[:k].mean(0)-arr[k:].mean(0)
            s=math.sqrt(k*(n-k)/n)*float(np.linalg.norm(d))
            if s>bv:bv=s;bk=k
        return bv,bk
    obs,k=best(z)
    blocks=[z[i:i+block] for i in range(0,len(z),block)]
    sims=[]
    for _ in range(nboot):
        order=RNG.permutation(len(blocks))
        zz=np.vstack([blocks[i] for i in order])[:len(z)]
        sims.append(best(zz)[0])
    p=float((1+sum(v>=obs for v in sims))/(nboot+1))
    return {"date":None if k is None else q.iloc[k].feature_cutoff_date.date().isoformat(),
            "score":float(obs),"block_permutation_p":p,"n":len(q),"columns":cols}

def main():
    f=pd.read_csv(F,parse_dates=["feature_cutoff_date"])
    pre=f[f.feature_cutoff_date<pd.Timestamp("2026-01-01")]
    q26=f[(f.feature_cutoff_date>=pd.Timestamp("2026-01-01"))&(f.feature_cutoff_date<=pd.Timestamp("2026-09-30"))].copy()
    m1,s1=robust_scale(pre,SHIFT);m2,s2=robust_scale(pre,STATE)
    shift=cp(q26,SHIFT,m1,s1)
    state=cp(q26,STATE,m2,s2)
    out={"schema":"GOLD_H3_DPTC_CHANGEPOINT_CORRECTION_V1_1","date":"2026-10-05",
         "correction":"Supersedes the invalid V1 2026-only changepoint that re-estimated scale on an empty pre-2026 subset.",
         "shift_vector_2026":shift,"topology_state_vector_2026":state,
         "calibration":"robust center/scale frozen on all pre-2026 origins","outcome_labels_used":False}
    OUTJ.write_text(json.dumps(out,indent=2)+"\n")
    lines=["# GOLD H3 — DPTC Change-Point Correction V1.1 — 2026-10-05","",
           "**Correction:** the V1 2026-only change-point line is invalid and is superseded here. Pre-2026 robust scale is frozen externally before examining the 2026 sequence.","",
           f"- Structural-shift vector change point: **{shift['date']}**, score **{shift['score']:.3f}**, block-permutation p **{shift['block_permutation_p']:.4f}**.",
           f"- Topology-state vector change point: **{state['date']}**, score **{state['score']:.3f}**, block-permutation p **{state['block_permutation_p']:.4f}**.","",
           "No competence labels are used in either change-point calculation."]
    OUTM.write_text("\n".join(lines)+"\n")
    print(OUTM.read_text())

if __name__=="__main__":main()
