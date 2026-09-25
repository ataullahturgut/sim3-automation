from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"; TR_START,TR_END="2025-01","2025-12"; ST_START,ST_END="2026-01","2026-07"

class ELM:
    def __init__(self,n_hidden=20,activation="tanh",alpha=1e-2,seed=1701):
        self.n_hidden=n_hidden; self.activation=activation; self.alpha=alpha; self.seed=seed
    def _act(self,z):
        if self.activation=="tanh": return np.tanh(z)
        if self.activation=="sigmoid": return 1/(1+np.exp(-np.clip(z,-40,40)))
        if self.activation=="relu": return np.maximum(z,0)
        raise ValueError(self.activation)
    def fit(self,X,Y):
        rng=np.random.default_rng(self.seed)
        d=X.shape[1]
        self.W=rng.normal(0,1/np.sqrt(d),size=(d,self.n_hidden))
        self.b=rng.normal(0,0.5,size=(self.n_hidden,))
        H=self._act(X@self.W+self.b)
        A=H.T@H + self.alpha*np.eye(self.n_hidden)
        B=H.T@Y
        try: self.beta=np.linalg.solve(A,B)
        except np.linalg.LinAlgError: self.beta=np.linalg.pinv(A)@B
        return self
    def predict(self,X):
        return self._act(X@self.W+self.b)@self.beta

def arrays(samples,t):
    ks=sorted(k for k in samples if k<t)
    if len(ks)<24: raise RuntimeError(f"TRAIN_TOO_SMALL {t}")
    X=np.stack([samples[k][0] for k in ks]); Y=np.stack([samples[k][1] for k in ks]); tx=samples[t][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    return ks,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def predict(samples,t,spec):
    hidden,act,alpha=spec
    ks,X,Y,tx,ym,ys=arrays(samples,t)
    m=ELM(hidden,act,alpha,seed=1701+sum(map(ord,t))).fit(X,Y)
    p=m.predict(tx)[0]*ys+ym
    return p,len(ks)

def ev(b,cache,spec,a,z):
    rows=[]; errs=[]
    for t in base.month_range(a,z):
        p,n=predict(cache[t],t,spec); pm=base.month_shift(t,-1)
        rows.append({"target":t,"origin":pm,"spec":list(spec),"train_rows":n,
                     "pred_log_return_gold":float(p[0]),
                     "forecast":float(b.core_gold[pm]*math.exp(float(p[0]))),
                     "actual":float(b.core_gold[t]),"rw":float(b.core_gold[pm])})
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][pm]); errs.append(abs(float(p[0])-ar))
    return float(np.mean(errs)),rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    specs=[(h,act,a) for h in (8,16,32,64) for act in ("tanh","sigmoid","relu") for a in (1e-3,1e-2,1e-1,1.0)]
    cand=[]
    for s in specs:
        obj,rows=ev(b,cache,s,DEV_START,DEV_END)
        cand.append({"spec":list(s),"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
    cand.sort(key=lambda x:(x["dev_logret_mae"],str(x["spec"])))
    sb=cand[0]["spec"]; best=(int(sb[0]),sb[1],float(sb[2]))
    _,dev=ev(b,cache,best,DEV_START,DEV_END); _,tr=ev(b,cache,best,TR_START,TR_END); _,st=ev(b,cache,best,ST_START,ST_END)
    out={"model_id":"VW_MIDAS_ELM_BASELINE_V1",
         "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","selection_period":f"{DEV_START}..{DEV_END}","random_split":"NONE","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
         "selected_spec":sb,"candidates":cand,
         "dev":{"metrics":base.metrics(dev),"rows":dev},
         "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
         "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    Path("vw_midas_elm_baseline_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"selected_spec":sb,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
