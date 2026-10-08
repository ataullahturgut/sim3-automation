"""Read-only paired risk-score stress audit for frozen 2023-2025 predictions.

The normal distribution approximation and IID p-values are NOT used.
5-date moving-block percentile bands are descriptive on an opened archive
and are NOT data-snooping-adjusted confirmatory tests.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

AX=Path(__file__).resolve().parents[1]
SRC=AX/"GOLD_OVN_2022_WARMUP_GVZ_TAIL1_PREDICTIONS_2026-10-08.csv"
MODEL="HAR_GVZ"

def brier(g,name):
    return float(np.mean((g[name].to_numpy(float)-g.y.to_numpy(float))**2))

def main():
    z=pd.read_csv(SRC).sort_values("date").reset_index(drop=True)
    assert len(z)==769
    assert z.groupby("year").size().to_dict()=={2023:256,2024:259,2025:254}
    assert (z.gvzAsOf < z.date).all()
    assert (z.nextDate > z.date).all()
    assert set(z.year)=={2023,2024,2025}
    cutoff=float(np.sort(z.loc[z.year.le(2024),MODEL].to_numpy())[int(np.floor(.8*(515-1)))])
    assert abs(cutoff-0.14184363080752652)<1e-12
    print("Frozen DEV 80th forecast-probability quantile =",cutoff)
    for yr,g in z.groupby("year"):
        loss_base=brier(g,"p0")
        loss_model=brier(g,MODEL)
        loss_har=brier(g,"HAR")
        alerts=g[g[MODEL].ge(cutoff)]
        print(yr,": n=",len(g),"actual>=1%=",int(g.y.sum()),
              "Brier base/model/HAR=",loss_base,loss_model,loss_har,
              "delta(base-model)=",loss_base-loss_model,
              "alarms=",len(alerts),
              "detected>=1%=",int(alerts.y.sum()),
              "detected>=2%=",int(alerts.r.abs().ge(.02).sum()),
              "of",int(g.r.abs().ge(.02).sum()),
              "AUC>=1%=",float(roc_auc_score(g.y,g[MODEL])))
    # This is a verified archive-control, NOT untouched-OOS inference.
    g=z[z.year.eq(2025)]
    for half,section in [("H1",g[g.date.str[5:7].astype(int).le(6)]),
                         ("H2",g[g.date.str[5:7].astype(int).gt(6)])]:
        print("2025",half,": Brier base",brier(section,"p0"),
              "model",brier(section,MODEL))
    g=g.assign(absr=g.r.abs()).sort_values("absr",ascending=False)
    for count in (3,7):
        sub=g.iloc[count:]
        print("2025 remove largest",count,"Brier base",brier(sub,"p0"),
              "model",brier(sub,MODEL))
    # deterministic 5-day moving-block 4800 draws (same LCG as JS audit)
    state=20261008
    def rand():
        nonlocal state
        state=(1664525*state+1013904223)&0xffffffff
        return state/(2**32)
    for year,g in z.groupby("year"):
        g=g.reset_index(drop=True)
        n=len(g)
        a=(g.p0-g.y).to_numpy()**2-(g[MODEL]-g.y).to_numpy()**2
        b=(g.HAR-g.y).to_numpy()**2-(g[MODEL]-g.y).to_numpy()**2
        dist_a=[]
        dist_b=[]
        for _ in range(4800):
            samples=[]
            while len(samples)<n:
                start=int(rand()*n)
                samples.extend((start+j)%n for j in range(5))
            index=np.array(samples[:n],dtype=int)
            dist_a.append(float(a[index].mean()))
            dist_b.append(float(b[index].mean()))
        da=np.sort(dist_a)
        db=np.sort(dist_b)
        print(year,"Paired Brier delta vs baseline:",float(a.mean()),
              "block-95%:",float(da[120]),float(da[4679]),
              "vs HAR:",float(b.mean()),
              "block-95%:",float(db[120]),float(db[4679]))
    # Exact rare-event alert counts are a QA, not an approved decision rule.
    g=z[z.year.eq(2025)]
    alarm=g[g[MODEL].ge(cutoff)]
    assert (len(alarm),int(alarm.y.sum()),int(alarm.r.abs().ge(.02).sum()))==(113,30,7)
    print("STRESS AUDIT PASS")

if __name__=="__main__":
    main()
