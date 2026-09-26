from __future__ import annotations
import argparse,json,math,os
from pathlib import Path
import numpy as np, psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as eb
import vw_midas_elmfis_meta_batch_1_v1 as common
import vw_midas_anfis_meta_screen_v6 as av6

DEV_START,DEV_END=av6.DEV_START,av6.DEV_END; TR_START,TR_END=av6.TR_START,av6.TR_END; ST_START,ST_END=av6.ST_START,av6.ST_END
POP=common.POP_SIZE; GENS=common.SELECT_GENS; REPEATS=common.REPEATS; LO,HI=common.LOWER,common.UPPER; D=common.PARAM_DIM

def logistic_sequence(n,seed):
    rng=np.random.default_rng(seed); x=float(rng.uniform(.1,.9)); a=np.empty(n)
    for i in range(n): x=4*x*(1-x); a[i]=x
    return a

def init_chaotic(center,seed):
    z=logistic_sequence(POP*D,seed).reshape(POP,D); P=LO+z*(HI-LO); P[0]=center
    return P

def hho_phase(X,Y,seed,generations,center,Xv,Yv):
    rng=np.random.default_rng(seed); P=init_chaotic(center,seed); F=av6.pop_fit(P,X,Y)
    vb,vf=av6.val_pick(P,F,X,Y,Xv,Yv,None,math.inf)
    for t in range(generations):
        rabbit=P[int(np.argmin(F))].copy(); E1=2*(1-(t+1)/generations); mean=P.mean(0)
        NP=P.copy()
        for i in range(POP):
            E0=2*rng.random()-1; E=E1*E0; q=rng.random(); J=2*(1-rng.random())
            if abs(E)>=1:
                if q>=.5:
                    xr=P[int(rng.integers(0,POP))]; cand=xr-rng.random(D)*np.abs(xr-2*rng.random(D)*P[i])
                else: cand=(rabbit-mean)-rng.random(D)*(LO+rng.random(D)*(HI-LO))
            else:
                if rng.random()>=.5:
                    cand=rabbit-E*np.abs(J*rabbit-P[i])
                else:
                    Yc=rabbit-E*np.abs(J*rabbit-P[i])
                    levy=rng.standard_cauchy(D)*.01
                    Z=Yc+levy
                    cand=Yc if av6.train_loss(np.clip(Yc,LO,HI),X,Y)<=av6.train_loss(np.clip(Z,LO,HI),X,Y) else Z
            NP[i]=np.clip(cand,LO,HI)
        NF=av6.pop_fit(NP,X,Y); imp=NF<F; P[imp]=NP[imp]; F[imp]=NF[imp]
        vb,vf=av6.val_pick(P,F,X,Y,Xv,Yv,vb,vf)
    return vb,float(vf)

def mvo_phase(X,Y,seed,generations,center,Xv,Yv):
    rng=np.random.default_rng(seed); P=common.init_population(rng,center,refit=False); F=av6.pop_fit(P,X,Y)
    vb,vf=av6.val_pick(P,F,X,Y,Xv,Yv,None,math.inf)
    for t in range(generations):
        order=np.argsort(F); best=P[order[0]].copy()
        norm=(F.max()-F)/(F.max()-F.min()+1e-12)
        WEP=.2+.8*(t+1)/generations; TDR=1-((t+1)/generations)**(1/6)
        NP=P.copy()
        for i in range(POP):
            for j in range(D):
                if rng.random()<norm[i]:
                    donor=int(rng.choice(POP,p=(norm+1e-9)/(norm.sum()+1e-9*POP))); NP[i,j]=P[donor,j]
                if rng.random()<WEP:
                    step=TDR*((HI[j]-LO[j])*rng.random()+LO[j])
                    NP[i,j]=best[j]+step if rng.random()<.5 else best[j]-step
        NP=np.clip(NP,LO,HI); NF=av6.pop_fit(NP,X,Y)
        imp=NF<F; P[imp]=NP[imp]; F[imp]=NF[imp]
        vb,vf=av6.val_pick(P,F,X,Y,Xv,Yv,vb,vf)
    return vb,float(vf)

def select(samples,target,method):
    keys,Xr,Yr,txr,split=av6.raw_arrays(samples,target); Xtrr,Ytrr=Xr[:split],Yr[:split]
    xm,xs,ym,ys=av6.scale_fit(Xtrr,Ytrr); X=(Xtrr-xm)/xs; Y=(Ytrr-ym)/ys; Xv=(Xr[split:]-xm)/xs; Yv=(Yr[split:]-ym)/ys
    anchor=common.initial_theta(X); best=None
    for rep in range(REPEATS):
        seed=(771100 if method=="CHHHO" else 881100)+1009*rep+sum(map(ord,target))
        th,v=(hho_phase if method=="CHHHO" else mvo_phase)(X,Y,seed,GENS,anchor,Xv,Yv)
        if best is None or v<best[0]: best=(v,th,rep)
    v,th,rep=best
    epochs,chk=av6.choose_local_epochs(th,X,Y,Xv,Yv)
    ci,si=common.decode(th); craw=ci*xs[None,:]+xm[None,:]; sraw=si*xs[None,:]
    xfm,xfs,yfm,yfs=av6.scale_fit(Xr,Yr); theta=common.encode((craw-xfm[None,:])/xfs[None,:],sraw/xfs[None,:])
    Xf=(Xr-xfm)/xfs; Yf=(Yr-yfm)/yfs; c,l,b,ld=av6.local_refit(theta,Xf,Yf,epochs)
    p=(av6.acore.design((txr-xfm)/xfs,c,l)@b)[0]*yfs+yfm
    return p,len(keys),{"selected_repeat":rep,"meta_check_fitness":v,"selected_local_epochs":epochs,"local_check_mse":chk,**ld}

def evaluate(b,cache,method,a,z):
    rows=[]
    for t in base.month_range(a,z):
        p,n,d=select(cache[t],t,method); o=base.month_shift(t,-1)
        rows.append({"target":t,"origin":o,"method":method,"train_rows":n,"diag":d,"pred_log_return_gold":float(p[0]),
          "forecast":float(b.core_gold[o]*math.exp(float(p[0]))),"actual":float(b.core_gold[t]),"rw":float(b.core_gold[o])})
    return rows

def inv(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
      with cn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def run(method):
    dsn=os.environ["NEON_DATABASE_URL"]; b=base.load_data(dsn); cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(b,cache,method,DEV_START,DEV_END); tr=evaluate(b,cache,method,TR_START,TR_END); st=evaluate(b,cache,method,ST_START,ST_END)
    if inv(dsn)!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={"model_id":f"VW_MIDAS_{method}_ANFIS_V1","method":method,"authority":{"database_access":"READ_ONLY","random_split":"NONE","target_month_in_training":False,"selection_period":f"{DEV_START}..{DEV_END}","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},"dev":{"metrics":eb.active_metrics(dev),"yearly":eb.yearly(dev),"rows":dev},"transport_2025":{"metrics":eb.active_metrics(tr),"rows":tr},"stress_2026":{"metrics":eb.active_metrics(st),"rows":st}}
    Path(f"anfis_stage3c_{method.lower()}_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS"); print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--method",choices=["CHHHO","MVO"],required=True); run(ap.parse_args().method)
