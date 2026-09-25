from __future__ import annotations

import json, math, os
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TRANSPORT_START, TRANSPORT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

def dist2(X,Z):
    return np.maximum(np.sum(X*X,1)[:,None]+np.sum(Z*Z,1)[None,:]-2*X@Z.T,0.0)

def design(X1,X2,width):
    K=np.exp(-(1.0/(width*width))*dist2(X1,X2))
    return np.column_stack([np.ones(len(X1)),K])

class FMRVR:
    # Direct algorithmic port of Youngmin Ha's public fmrvr.m v1.2.0.0.
    def __init__(self,width=1.6,max_iters=500,tolerance=0.1,seed=7):
        self.width=float(width); self.max_iters=int(max_iters)
        self.tolerance=float(tolerance); self.seed=int(seed)

    def fit(self,X,T):
        rng=np.random.default_rng(self.seed)
        Phi=design(X,X,self.width)
        N,V=T.shape
        assert Phi.shape==(N,N+1)
        Om=0.1*np.cov(T,rowvar=False)
        if np.ndim(Om)==0: Om=np.array([[float(Om)]])
        Om=0.5*(Om+Om.T)+1e-8*np.eye(V)
        alpha=np.full(N+1,np.inf)
        mask=np.zeros(N+1,dtype=bool)
        PhiMask=np.empty((N,0)); Mu=np.empty((0,V)); invSigma=np.empty((0,0))
        PhiSigmaPhi=np.zeros((N,N))
        iter_num=0
        for it in range(1,self.max_iters+1):
            iter_num=it
            sPrime=np.full(N+1,np.nan); qPrime=np.full((N+1,V),np.nan)
            s=np.full(N+1,np.nan); q=np.full((N+1,V),np.nan)
            all_inf=not mask.any()
            for i in range(N+1):
                ph=Phi[:,i]
                if all_inf:
                    sp=float(ph@ph); qp=ph@T
                else:
                    sp=float(ph@ph - ph@PhiSigmaPhi@ph)
                    qp=ph@T - ph@PhiSigmaPhi@T
                sPrime[i]=sp; qPrime[i]=qp
                if not mask[i]:
                    s[i]=sp; q[i]=qp
                else:
                    den=alpha[i]-sp
                    if abs(den)<1e-14: den=np.copysign(1e-14,den if den!=0 else 1)
                    tmp=alpha[i]/den
                    s[i]=tmp*sp; q[i]=tmp*qp

            try: invOm=np.linalg.inv(Om)
            except np.linalg.LinAlgError: invOm=np.linalg.pinv(Om)
            delta=np.full(N+1,np.nan)
            task=np.array(["non"]*(N+1),dtype=object)
            theta=np.zeros(N+1); alpha_new=np.full(N+1,np.nan)
            for i in range(N+1):
                qi=q[i][None,:]
                theta[i]=float(np.trace(invOm@(qi.T@qi))/V - s[i])
                qpi=qPrime[i][None,:]
                qpsq=float(np.trace(invOm@(qpi.T@qpi)))
                if theta[i]>0:
                    if mask[i]:
                        task[i]="est"; alpha_new[i]=(s[i]**2)/theta[i]
                        if alpha_new[i]!=0:
                            temp=1.0/alpha_new[i]-1.0/alpha[i]
                            den=sPrime[i]+1.0/temp if abs(temp)>1e-14 else np.nan
                            arg=1.0+sPrime[i]*temp
                            delta[i]=qpsq/den - V*np.log(arg) if den!=0 and arg>0 else -np.inf
                        else: delta[i]=-np.inf
                    else:
                        task[i]="add"
                        if sPrime[i]>1e-14 and qpsq>0:
                            temp=qpsq/sPrime[i]
                            delta[i]=temp-V+V*np.log(V/temp) if temp>0 else -np.inf
                        else: delta[i]=-np.inf
                elif mask[i]:
                    task[i]="del"
                    den=sPrime[i]-alpha[i]; arg=1.0-sPrime[i]/alpha[i]
                    delta[i]=qpsq/den - V*np.log(arg) if abs(den)>1e-14 and arg>0 else -np.inf

            valid=np.where(~np.isnan(delta))[0]
            if len(valid)==0: break
            finite_or_inf=delta[valid]
            if np.all(np.isneginf(finite_or_inf)):
                actionable=valid[np.array([task[j]!="non" for j in valid])]
                if len(actionable)==0: break
                i=int(rng.choice(actionable))
            else:
                i=int(valid[np.nanargmax(finite_or_inf)])

            converged=False
            if task[i]=="est":
                change=np.log(alpha[i]/alpha_new[i])
                alpha[i]=alpha_new[i]
                if abs(change)<self.tolerance and np.all(theta[~mask]<=0):
                    converged=True
            elif task[i]=="add":
                alpha[i]=(s[i]**2)/theta[i]; mask[i]=True
            elif task[i]=="del":
                alpha[i]=np.inf; mask[i]=False
            else:
                break

            if it!=1 and PhiMask.shape[1]>0:
                Om=T.T@(T-PhiMask@Mu)/N
                Om=0.5*(Om+Om.T)+1e-8*np.eye(V)

            PhiMask=Phi[:,mask]
            if PhiMask.shape[1]==0:
                PhiSigmaPhi=np.zeros((N,N)); Mu=np.empty((0,V)); invSigma=np.empty((0,0))
            else:
                invSigma=PhiMask.T@PhiMask+np.diag(alpha[mask])
                try: SigmaPhi=np.linalg.solve(invSigma,PhiMask.T)
                except np.linalg.LinAlgError: SigmaPhi=np.linalg.pinv(invSigma)@PhiMask.T
                Mu=SigmaPhi@T
                PhiSigmaPhi=PhiMask@SigmaPhi
            if converged: break

        self.X_train=np.asarray(X,float).copy()
        self.used=np.where(mask)[0]
        self.Mu=Mu; self.Omega=Om; self.invSigma=invSigma; self.n_iters=iter_num
        if len(self.used)==0: raise RuntimeError("FMRVR_NO_RELEVANCE_VECTORS")
        return self

    def predict(self,X):
        Phi=design(np.asarray(X,float),self.X_train,self.width)
        return Phi[:,self.used]@self.Mu

def arrays(samples,target):
    keys=sorted(k for k in samples if k<target)
    if len(keys)<24: raise RuntimeError(f"TRAINING_ROWS_TOO_FEW {target}")
    X=np.stack([samples[k][0] for k in keys]); Y=np.stack([samples[k][1] for k in keys])
    tx=samples[target][0][None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    return keys,(X-xm)/xs,(Y-ym)/ys,(tx-xm)/xs,ym,ys

def fit_predict(samples,target,width):
    keys,X,Y,tx,ym,ys=arrays(samples,target)
    m=FMRVR(width=width,max_iters=500,tolerance=0.1,seed=7+sum(map(ord,target))).fit(X,Y)
    pred=m.predict(tx)[0]*ys+ym
    return pred,len(keys),len(m.used),m.n_iters

def make_row(b,t,pred,n,nrv,nit,width):
    p=base.month_shift(t,-1)
    return {"target":t,"origin":p,"kernel_width":width,"train_rows":n,
            "relevance_vectors":nrv,"iterations":nit,
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
            "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p])}

def eval_width(b,cache,width,start,end):
    rows=[]; errs=[]
    for t in base.month_range(start,end):
        pred,n,nrv,nit=fit_predict(cache[t],t,width)
        rows.append(make_row(b,t,pred,n,nrv,nit,width))
        p=base.month_shift(t,-1)
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][p])
        errs.append(abs(float(pred[0])-ar))
    return float(np.mean(errs)),rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True)
           for t in base.month_range(DEV_START,STRESS_END)}
    widths=(0.5,1.0,1.6,2.5)
    cand=[]
    saved={}
    for w in widths:
        obj,rows=eval_width(b,cache,w,DEV_START,DEV_END)
        saved[w]=rows
        cand.append({"width":w,"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
    cand.sort(key=lambda z:(z["dev_logret_mae"],z["width"]))
    best=float(cand[0]["width"])
    dev=saved[best]
    _,tr=eval_width(b,cache,best,TRANSPORT_START,TRANSPORT_END)
    _,st=eval_width(b,cache,best,STRESS_START,STRESS_END)
    result={
      "model_id":"VW_MIDAS_FMRVR_V1",
      "method_binding":{"author":"Youngmin Ha","source":"public fmrvr.m v1.2.0.0",
                        "port":"DIRECT_ALGORITHMIC_PYTHON_PORT","kernel":"+gauss"},
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                   "selection_period":f"{DEV_START}..{DEV_END}",
                   "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
                   "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
      "source_checks":b.source_checks,"candidates":cand,"selected_width":best,
      "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
      "stress_2026":{"metrics":base.metrics(st),"rows":st},
    }
    Path("vw_midas_fmrvr_v1_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"selected_width":best,
                      "dev":result["dev"]["metrics"],
                      "transport_2025":result["transport_2025"]["metrics"],
                      "stress_2026":result["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__": main()
