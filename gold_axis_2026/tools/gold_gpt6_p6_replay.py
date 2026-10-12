"""Exact GP RBF posterior on the last 40 origin-safe sessions versus current-price RW.
Verifies historical issue MID at issue-15min (not future 09/16:45 entry), every price forecast.
"""
import csv,math,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parents[1]
def read(name):
    with (D/name).open(newline="") as f:return list(csv.DictReader(f))
def models(train,r):
    cols=("L1","L5","L22","V1")
    x=np.array([[u[k] for k in cols] for u in train],float)
    y=np.array([u["r"] for u in train],float)
    ym=y.mean();avg=x.mean(0);sd=x.std(0);sd[sd<1e-10]=1.
    z=(x-avg)/sd
    now=(np.array([r[k] for k in cols])-avg)/sd
    beta=np.linalg.solve(z.T@z+10*np.eye(4),z.T@(y-ym))
    ridge=float(ym+now@beta)
    dd=((z[:,None,:]-z[None,:,:])**2).sum(axis=2)
    K=np.exp(-0.5*dd)+np.eye(len(train))
    alpha=np.linalg.solve(K,y-ym)
    kstar=np.exp(-0.5*((z-now)**2).sum(axis=1))
    gp=float(ym+kstar@alpha)
    return {"RW":0., "MEAN40":float(ym),"RIDGE":ridge,"GPR":gp}
def main():
    raw=read("GOLD_GPT6_P6_ASOF_PRICE_TARGET_SOURCE.csv")
    assert len(raw)==2740
    source=[{"date":r["date"],"sn":r["sn"],"year":int(r["year"]),
          "rv":float(r["rv"]),"r":float(r["r"]),
          "known_issue_price":float(r["known_issue_price"]),
          "future_exit":float(r["future_exit"])} for r in raw]
    scores={}
    for sn in ("DAY","OVN"):
        a=read("GOLD_GPT6_P6_GPR_SCORE_"+sn+".csv")
        scores[sn]={r["date"]:r for r in a}
    assert sum(map(len,scores.values()))==1366
    verified=0
    for sn in ("DAY","OVN"):
        sessions=sorted((r for r in source if r["sn"]==sn),key=lambda r:r["date"])
        features=[]
        for i in range(22,len(sessions)):
            history=sessions[:i]
            returns=np.array([u["r"] for u in history])
            current=sessions[i].copy()
            current.update(L1=float(returns[-1]),L5=float(returns[-5:].mean()),
                           L22=float(returns[-22:].mean()),V1=math.log(history[-1]["rv"]))
            assert abs(math.log(current["future_exit"]/current["known_issue_price"])-current["r"])<1e-10
            features.append(current)
        for i in range(40,len(features)):
            r=features[i]
            if r["year"]<2023:continue
            h=features[i-40:i]
            m=models(h,r)
            expected=scores[sn][r["date"]]
            assert int(expected["train_n"])==40
            assert abs(r["known_issue_price"]-float(expected["issue"]))<1e-9
            for name,pred in m.items():
                price=r["known_issue_price"]*math.exp(pred)
                found={"ret":pred,"price":price,
                       "price_ae":abs(price-r["future_exit"]),
                       "price_se":(price-r["future_exit"])**2,
                       "r_se":(pred-r["r"])**2,"bit":int(pred>0)}
                for key,value in found.items():
                    assert math.isclose(value,float(expected[name+"_"+key]),rel_tol=1e-8,abs_tol=1e-7),(r["date"],sn,name,key)
            verified+=1
    assert verified==1366
    summ=json.loads((D/"GOLD_GPT6_P6_RESULT.json").read_text())
    assert summ["verdict"]=="REJECT_NO_PROMOTION"
    assert not any(summ["gates"].values())
    print("P6 PASS 2740 as-of source rows, exact RBF GP + Ridge 1366 full future prices. RW wins.")
if __name__=="__main__":main()
