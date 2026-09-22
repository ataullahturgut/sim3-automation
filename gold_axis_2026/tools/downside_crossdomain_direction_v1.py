from __future__ import annotations

import csv, json, math, os, hashlib
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from scipy.optimize import minimize
from scipy.special import expit, logsumexp
from scipy.stats import rankdata
from sklearn.linear_model import HuberRegressor

IDENTITY="DOWNSIDE_CROSSDOMAIN_DIRECTION_V1_RESEARCH"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
YEARS=(2022,2023,2024,2025,2026)
PRE=(2022,2023,2024)
EPS=1e-12

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,float); k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_days():
    sql=f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date d,
        observation_ts,
        close::double precision close,
        lag(close::double precision) over(
          partition by (observation_ts at time zone '{TZ}')::date order by observation_ts
        ) prev_close
      from {TABLE}
      where extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    r as (
      select d,observation_ts,close,
             case when prev_close>0 then ln(close/prev_close) end ret
      from b
    ),
    a as (
      select d,count(*)::int bars,
             (array_agg(close order by observation_ts desc))[1]::double precision close,
             sum(case when ret<0 then ret*ret else 0 end)::double precision dr
      from r group by d
    )
    select d,bars,close,dr from a where bars>=240 order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql); raw=cur.fetchall()
    ds=[];c=[];dr=[]
    for d,bars,cl,x in raw:
        cl=float(cl);x=float(x)
        if not(cl>0 and x>0 and math.isfinite(cl) and math.isfinite(x)): raise RuntimeError(f"BAD_DAY:{d}")
        ds.append(d);c.append(cl);dr.append(x)
    return ds,np.asarray(c,float),np.asarray(dr,float)

def panel_hash(ds,c,dr):
    s="\n".join(f"{d.isoformat()}|{x:.12f}|{v:.16g}" for d,x,v in zip(ds,c,dr))
    return hashlib.sha256(s.encode()).hexdigest()

def build_rows(ds,c,dr):
    sd=np.sqrt(dr)
    dret=np.full(len(c),np.nan);dret[1:]=np.log(c[1:]/c[:-1])
    rows=[]
    for i in range(21,len(ds)-1):
        sd5=float(np.mean(sd[i-4:i+1])); sd22=float(np.mean(sd[i-21:i+1]))
        if sd5<=0 or sd22<=0: continue
        tr=float(dret[i+1])
        rows.append({
          "origin_idx":i,"target_idx":i+1,
          "origin_date":ds[i].isoformat(),"target_date":ds[i+1].isoformat(),
          "origin_return":float(dret[i]),
          "sd_d":float(sd[i]),"sd_w":sd5,"sd_m":sd22,
          "log_sd":float(math.log(sd[i])),
          "log_sd_vs_w":float(math.log(sd[i]/sd5)),
          "log_w_vs_m":float(math.log(sd5/sd22)),
          "target_return":tr,"target_down":int(tr<0),
          "target_dr":float(dr[i+1]),"target_sd":float(sd[i+1])
        })
    return rows,sd,dret

def feats(rows):
    return np.asarray([[r["origin_return"],r["log_sd"],r["log_sd_vs_w"],r["log_w_vs_m"]] for r in rows],float)

def standardize_fit(X):
    mu=X.mean(0);sd=X.std(0,ddof=1);sd=np.where(sd>1e-12,sd,1.0)
    return mu,sd

def add_intercept(X): return np.column_stack([np.ones(len(X)),X])

def logistic_fit(X,y):
    X=add_intercept(X);y=np.asarray(y,float)
    def fun(b):
        z=X@b
        return float(np.sum(np.logaddexp(0,z)-y*z)+5e-9*np.dot(b[1:],b[1:]))
    def jac(b):
        p=expit(X@b)
        g=X.T@(p-y);g[1:]+=1e-8*b[1:]
        return g
    res=minimize(fun,np.zeros(X.shape[1]),jac=jac,method="L-BFGS-B",options={"maxiter":3000,"ftol":1e-12})
    if not res.success: raise RuntimeError(f"LOGIT_FAIL:{res.message}")
    b=res.x;p=expit(X@b);w=np.clip(p*(1-p),1e-8,None)
    H=X.T@(w[:,None]*X)+np.diag([0]+[1e-8]*(X.shape[1]-1))
    C=np.linalg.pinv(H)
    return b,C

def multinom_fit(X,y):
    X=add_intercept(X);y=np.asarray(y,int);n,p=X.shape;K=3
    def unpack(t): return t.reshape(K-1,p)
    def fun(t):
        B=unpack(t)
        logits=np.column_stack([np.zeros(n),X@B.T])
        ll=logits[np.arange(n),y]-logsumexp(logits,axis=1)
        return float(-np.sum(ll)+5e-9*np.dot(t,t))
    def jac(t):
        B=unpack(t);logits=np.column_stack([np.zeros(n),X@B.T])
        P=np.exp(logits-logsumexp(logits,axis=1)[:,None])
        G=np.zeros_like(B)
        for k in range(1,K):
            G[k-1]=X.T@(P[:,k]-(y==k))
        return (G.ravel()+1e-8*t)
    res=minimize(fun,np.zeros((K-1)*p),jac=jac,method="L-BFGS-B",options={"maxiter":3000,"ftol":1e-12})
    if not res.success: raise RuntimeError(f"MULTINOM_FAIL:{res.message}")
    return res.x.reshape(K-1,p)

def multinom_predict(B,X):
    X=add_intercept(X);logits=np.column_stack([np.zeros(len(X)),X@B.T])
    P=np.exp(logits-logsumexp(logits,axis=1)[:,None])
    return P

def dynamic_logit_predict(b,C,X,y,delta=.99):
    X=add_intercept(X);b=b.copy();C=C.copy();out=[]
    for x,yy in zip(X,y):
        R=C/delta
        p=float(expit(x@b));out.append(p)
        w=max(p*(1-p),1e-6)
        Ri=np.linalg.pinv(R)
        C=np.linalg.pinv(Ri+w*np.outer(x,x))
        b=b+C@x*(float(yy)-p)
        C=(C+C.T)*0.5
    return np.asarray(out,float)

def auc(y,s):
    y=np.asarray(y,int);s=np.asarray(s,float)
    n1=int(np.sum(y==1));n0=int(np.sum(y==0))
    if not n1 or not n0:return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def cls_metrics(y,p):
    y=np.asarray(y,int);p=np.asarray(p,float);pred=p>=.5
    tp=int(np.sum(pred&(y==1)));fp=int(np.sum(pred&(y==0)));fn=int(np.sum((~pred)&(y==1)));tn=int(np.sum((~pred)&(y==0)))
    sens=tp/(tp+fn) if tp+fn else None;spec=tn/(tn+fp) if tn+fp else None
    prec=tp/(tp+fp) if tp+fp else None
    return {
      "n":len(y),"actual_down":int(np.sum(y)),"down_calls":int(np.sum(pred)),
      "tp":tp,"fp":fp,"fn":fn,"tn":tn,
      "accuracy":float(np.mean(pred==y)),
      "balanced_accuracy":float((sens+spec)/2) if sens is not None and spec is not None else None,
      "roc_auc":auc(y,p),
      "brier":float(np.mean((p-y)**2)),
      "log_loss":float(-np.mean(y*np.log(np.clip(p,EPS,1-EPS))+(1-y)*np.log(np.clip(1-p,EPS,1-EPS)))),
      "down_precision":prec,"down_recall":sens,"specificity":spec,"down_call_rate":float(np.mean(pred))
    }

def highrisk_metrics(y,p,mask):
    y=np.asarray(y,int)[mask];p=np.asarray(p,float)[mask]
    return cls_metrics(y,p) if len(y) else None

def state_label(sd,q50,q80):
    if sd<q50:return "LOW"
    if sd<q80:return "ELEVATED"
    return "HIGH"

def semimarkov_probs(all_rows,train_mask,test_mask,q50,q80):
    states=[];durs=[];last=None;dur=0
    for r in all_rows:
        st=state_label(r["sd_d"],q50,q80)
        if st==last: dur+=1
        else: last=st;dur=1
        states.append(st);durs.append(dur)
    train_idx=np.where(train_mask)[0];test_idx=np.where(test_mask)[0]
    # count dictionaries [down,total]
    full={};sdict={};rdict={};global_d=0;global_n=0
    def add(dic,key,y):
        a=dic.setdefault(key,[0,0]);a[0]+=int(y);a[1]+=1
    for i in train_idx:
        r=all_rows[i];sgn="U" if r["origin_return"]>=0 else "D";db=1 if durs[i]==1 else (2 if durs[i]==2 else 3);y=r["target_down"]
        add(full,(states[i],sgn,db),y);add(sdict,(states[i],sgn),y);add(rdict,states[i],y)
        global_d+=y;global_n+=1
    out=[]
    for i in test_idx:
        r=all_rows[i];sgn="U" if r["origin_return"]>=0 else "D";db=1 if durs[i]==1 else (2 if durs[i]==2 else 3)
        key=(states[i],sgn,db)
        if key in full and full[key][1]>=10: d,n=full[key]
        elif (states[i],sgn) in sdict and sdict[(states[i],sgn)][1]>=20: d,n=sdict[(states[i],sgn)]
        elif states[i] in rdict and rdict[states[i]][1]>=30: d,n=rdict[states[i]]
        else: d,n=global_d,global_n
        out.append((d+1)/(n+2))
    return np.asarray(out,float)

def sqrt_har_fit(train):
    X=np.asarray([[r["sd_d"],r["sd_w"],r["sd_m"]] for r in train],float);y=np.asarray([r["target_sd"] for r in train])
    Z=add_intercept(X);b=np.linalg.lstsq(Z,y,rcond=None)[0]
    return b

def sqrt_har_pred(rows,b):
    X=np.asarray([[r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],float)
    z=add_intercept(X)@b
    if np.any(z<=0): raise RuntimeError("SQRT_DOMAIN")
    return z*z

def huber_sqrt_fit(train):
    X=np.asarray([[r["sd_d"],r["sd_w"],r["sd_m"]] for r in train],float);y=np.asarray([r["target_sd"] for r in train])
    mu=X.mean(0);sc=X.std(0,ddof=1);sc=np.where(sc>1e-12,sc,1.0)
    model=HuberRegressor(epsilon=1.35,alpha=0.0,fit_intercept=True,max_iter=5000,tol=1e-10)
    model.fit((X-mu)/sc,y)
    return model,mu,sc

def huber_sqrt_pred(rows,fit):
    model,mu,sc=fit;X=np.asarray([[r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],float)
    z=model.predict((X-mu)/sc)
    if np.any(z<=0): raise RuntimeError("HUBER_DOMAIN")
    return z*z

def qlike(y,p):
    z=np.asarray(y)/np.asarray(p)
    return float(np.mean(z-np.log(z)-1))

def risk_metrics(rows,p,mean_dr,hi):
    y=np.asarray([r["target_dr"] for r in rows]);ret=np.asarray([r["target_return"] for r in rows])
    mse=float(np.mean((p-y)**2));bm=float(np.mean((mean_dr-y)**2));high=(y>=hi).astype(int);alert=p>=hi
    Z=np.column_stack([np.ones(len(p)),p]);cal=np.linalg.lstsq(Z,y,rcond=None)[0]
    tp=int(np.sum(alert&(high==1)));fp=int(np.sum(alert&(high==0)));fn=int(np.sum((~alert)&(high==1)))
    prec=tp/(tp+fp) if tp+fp else None;rec=tp/(tp+fn) if tp+fn else None
    return {"n":len(y),"mse":mse,"mae":float(np.mean(np.abs(p-y))),"oos_r2":float(1-mse/bm),"qlike":qlike(y,p),
            "calibration_slope":float(cal[1]),"calibration_error":abs(float(cal[1])-1),
            "auc":auc(high,p),"precision":prec,"recall":rec,"coverage":float(np.mean(alert)),
            "down_rate_given_alert":float(np.mean(ret[alert]<0)) if np.sum(alert) else None}

def eval_year(all_rows,year):
    cutoff=date(year-1,12,31)
    train_mask=np.array([date.fromisoformat(r["target_date"])<=cutoff for r in all_rows])
    test_mask=np.array([date.fromisoformat(r["target_date"]).year==year for r in all_rows])
    train=[r for r,m in zip(all_rows,train_mask) if m];test=[r for r,m in zip(all_rows,test_mask) if m]
    if len(train)<250 or not test: raise RuntimeError(f"SUPPORT:{year}:{len(train)}:{len(test)}")
    Xtr=feats(train);Xte=feats(test);mu,sc=standardize_fit(Xtr);A=(Xtr-mu)/sc;B=(Xte-mu)/sc
    ytr=np.asarray([r["target_down"] for r in train],int);yte=np.asarray([r["target_down"] for r in test],int)

    b,C=logistic_fit(A,ytr);p_static=expit(add_intercept(B)@b)
    p_dynamic=dynamic_logit_predict(b,C,B,yte,.99)

    ext=nearest_rank(np.asarray([r["target_return"] for r in train]),.05)
    y3=np.array([0 if r["target_return"]>=0 else (2 if r["target_return"]<=ext else 1) for r in train],int)
    MB=multinom_fit(A,y3);P=multinom_predict(MB,B);p_comp=P[:,1]+P[:,2]

    q50=nearest_rank(np.asarray([r["sd_d"] for r in train]),.50);q80sd=nearest_rank(np.asarray([r["sd_d"] for r in train]),.80)
    p_semi=semimarkov_probs(all_rows,train_mask,test_mask,q50,q80sd)

    sb=sqrt_har_fit(train);p_sqrt=sqrt_har_pred(test,sb)
    hb=huber_sqrt_fit(train);p_huber=huber_sqrt_pred(test,hb)
    mean_dr=float(np.mean([r["target_dr"] for r in train]));hi=nearest_rank(np.asarray([r["target_dr"] for r in train]),.80)
    highmask=p_sqrt>=hi

    models={"STATIC_LOGIT":p_static,"DYNAMIC_LOGIT_D99":p_dynamic,"COMPETING_RISK_MULTINOMIAL":p_comp,"EXPLICIT_DURATION_TRANSITION":p_semi}
    full={k:cls_metrics(yte,p) for k,p in models.items()}
    bridge={k:highrisk_metrics(yte,p,highmask) for k,p in models.items()}
    ref=cls_metrics(yte[highmask],np.ones(int(np.sum(highmask)))) if np.sum(highmask) else None

    risk={"SQRT_HAR_DR":risk_metrics(test,p_sqrt,mean_dr,hi),"HUBER_SQRT_HAR":risk_metrics(test,p_huber,mean_dr,hi)}
    rowsout=[]
    for j,r in enumerate(test):
        rowsout.append({"target_date":r["target_date"],"evaluation_year":year,"target_down":int(yte[j]),"target_return":r["target_return"],
                        "sqrt_high_risk_alert":int(highmask[j]),"sqrt_forecast_dr":float(p_sqrt[j]),"huber_forecast_dr":float(p_huber[j]),
                        "static_p_down":float(p_static[j]),"dynamic_p_down":float(p_dynamic[j]),"competing_p_down":float(p_comp[j]),"semimarkov_p_down":float(p_semi[j])})
    return {"formation_n":len(train),"test_n":len(test),"formation_cutoff":cutoff.isoformat(),"extreme_q05":ext,
            "sd_q50":q50,"sd_q80":q80sd,"high_risk_threshold_dr":hi,
            "full_direction":full,"high_risk_bridge":bridge,"all_high_risk_as_down":ref,"risk_models":risk},rowsout

def pooled_cls(rows,key):
    y=np.array([r["target_down"] for r in rows],int);p=np.array([r[key] for r in rows],float)
    return cls_metrics(y,p)

def pooled_bridge(rows,key):
    z=[r for r in rows if int(r["sqrt_high_risk_alert"])==1]
    y=np.array([r["target_down"] for r in z],int);p=np.array([r[key] for r in z],float)
    return cls_metrics(y,p),cls_metrics(y,np.ones(len(y)))

def pooled_risk(rows,key):
    y=np.array([float(r["target_dr"]) for r in rows]) if "target_dr" in rows[0] else None
    return None

def main():
    out=Path("crossdomain_out");out.mkdir(exist_ok=True)
    ds,c,dr=load_days();all_rows,sd,dret=build_rows(ds,c,dr)
    years={};predrows=[]
    for y in YEARS:
        b,rr=eval_year(all_rows,y);years[str(y)]=b;predrows+=rr
        print(json.dumps({"year":y,"alerts":b["all_high_risk_as_down"]["n"],
          "ref_fp":b["all_high_risk_as_down"]["fp"],
          "static_fp":b["high_risk_bridge"]["STATIC_LOGIT"]["fp"],
          "dynamic_fp":b["high_risk_bridge"]["DYNAMIC_LOGIT_D99"]["fp"],
          "competing_fp":b["high_risk_bridge"]["COMPETING_RISK_MULTINOMIAL"]["fp"],
          "semi_fp":b["high_risk_bridge"]["EXPLICIT_DURATION_TRANSITION"]["fp"],
          "huber_mse":b["risk_models"]["HUBER_SQRT_HAR"]["mse"]},sort_keys=True))

    pre=[r for r in predrows if int(r["evaluation_year"]) in PRE]
    mapping={"STATIC_LOGIT":"static_p_down","DYNAMIC_LOGIT_D99":"dynamic_p_down","COMPETING_RISK_MULTINOMIAL":"competing_p_down","EXPLICIT_DURATION_TRANSITION":"semimarkov_p_down"}
    pooled={}
    decisions={}
    for name,key in mapping.items():
        full=pooled_cls(pre,key);bridge,ref=pooled_bridge(pre,key)
        annual_nonworse=sum((years[str(y)]["high_risk_bridge"][name]["balanced_accuracy"] or 0)>=(years[str(y)]["all_high_risk_as_down"]["balanced_accuracy"] or 0) for y in PRE)
        supported=bool(full["balanced_accuracy"]>0.52 and full["roc_auc"]>0.55 and bridge["fp"]<ref["fp"] and bridge["down_recall"]>=0.70*ref["down_recall"] and annual_nonworse>=2)
        pooled[name]={"full":full,"high_risk_bridge":bridge,"reference":ref,"annual_highrisk_nonworse_count":annual_nonworse}
        decisions[name]="RETROSPECTIVE_DIRECTION_BRIDGE_SUPPORTED" if supported else "RETROSPECTIVE_DIRECTION_BRIDGE_NOT_SUPPORTED"

    # pooled robust-risk metrics computed directly from yearly weighted errors/qlike; annual gates are primary
    huber_mse_wins=sum(years[str(y)]["risk_models"]["HUBER_SQRT_HAR"]["mse"]<years[str(y)]["risk_models"]["SQRT_HAR_DR"]["mse"] for y in PRE)
    huber_cal_wins=sum(years[str(y)]["risk_models"]["HUBER_SQRT_HAR"]["calibration_error"]<years[str(y)]["risk_models"]["SQRT_HAR_DR"]["calibration_error"] for y in PRE)
    huber_auc_ok=all(years[str(y)]["risk_models"]["HUBER_SQRT_HAR"]["auc"]>=years[str(y)]["risk_models"]["SQRT_HAR_DR"]["auc"]-.02 for y in PRE)
    # weighted pooled from yearly sums is exact because annual n are known
    ns=np.array([years[str(y)]["test_n"] for y in PRE],float)
    sq_mse=sum(years[str(y)]["risk_models"]["SQRT_HAR_DR"]["mse"]*years[str(y)]["test_n"] for y in PRE)/sum(ns)
    hu_mse=sum(years[str(y)]["risk_models"]["HUBER_SQRT_HAR"]["mse"]*years[str(y)]["test_n"] for y in PRE)/sum(ns)
    sq_q=sum(years[str(y)]["risk_models"]["SQRT_HAR_DR"]["qlike"]*years[str(y)]["test_n"] for y in PRE)/sum(ns)
    hu_q=sum(years[str(y)]["risk_models"]["HUBER_SQRT_HAR"]["qlike"]*years[str(y)]["test_n"] for y in PRE)/sum(ns)
    huber_supported=bool(huber_mse_wins>=2 and hu_mse<sq_mse and hu_q<=sq_q and huber_cal_wins>=2 and huber_auc_ok)

    result={"identity":IDENTITY,"manifest_modified":False,"production_write":"NONE",
      "evidence_classification":"RETROSPECTIVE_ONLY_NOT_PRISTINE_CONFIRMATION",
      "panel_first_day":ds[0].isoformat(),"panel_last_day":ds[-1].isoformat(),"panel_sha256":panel_hash(ds,c,dr),
      "years":years,"pooled_2022_2024_direction":pooled,"direction_decisions":decisions,
      "huber_gate":{"mse_wins":huber_mse_wins,"calibration_wins":huber_cal_wins,"auc_tolerance_all":huber_auc_ok,
                    "pooled_sqrt_mse":sq_mse,"pooled_huber_mse":hu_mse,"pooled_sqrt_qlike":sq_q,"pooled_huber_qlike":hu_q,
                    "decision":"RETROSPECTIVE_ROBUST_RISK_SUPPORTED" if huber_supported else "RETROSPECTIVE_ROBUST_RISK_NOT_SUPPORTED"}}
    (out/"GOLD_CONTROL_DOWNSIDE_CROSSDOMAIN_DIRECTION_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))
    with open(out/"GOLD_CONTROL_DOWNSIDE_CROSSDOMAIN_DIRECTION_V1_FORECASTS_2026-09-22.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(predrows[0].keys()));w.writeheader();w.writerows(predrows)
    lines=["# GOLD CONTROL — CROSS-DOMAIN DOWNSIDE / DIRECTION V1 RESULT","",
      "**Manifest modified:** NO  ","",
      "| Method | Pooled 2022-24 BA | AUC | High-risk FP | High-risk TP | High-risk recall | Decision |",
      "|---|---:|---:|---:|---:|---:|---|"]
    for name in mapping:
        p=pooled[name]
        lines.append(f"| {name} | {p['full']['balanced_accuracy']:.4f} | {p['full']['roc_auc']:.4f} | {p['high_risk_bridge']['fp']} | {p['high_risk_bridge']['tp']} | {p['high_risk_bridge']['down_recall']:.4f} | {decisions[name]} |")
    lines+=["",f"**Huber risk decision:** {result['huber_gate']['decision']}  "]
    (out/"GOLD_CONTROL_DOWNSIDE_CROSSDOMAIN_DIRECTION_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("CROSSDOMAIN_SUCCESS")

if __name__=="__main__": main()
