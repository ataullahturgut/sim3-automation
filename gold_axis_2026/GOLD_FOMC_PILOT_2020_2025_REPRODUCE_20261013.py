#!/usr/bin/env python3
"""FOMC 2020-25 explanatory event study; stdlib-only replication from derived event CSV.
No new data downloads, no forecast, no causal identification by OLS.
Run: python gold_axis_2026/GOLD_FOMC_PILOT_2020_2025_REPRODUCE_20261013.py
"""
import csv, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NAME="GOLD_FOMC_PILOT_2020_2025_EVENT_LEVEL_V1_20261013.csv"
with (ROOT/NAME).open(newline="",encoding="utf8") as handle:
    raw=list(csv.DictReader(handle))
events=[dict(year=int(r["year"]), x=float(r["path_surprise_bp"])/10,
             mp1=float(r["mp1_surprise_bp"])/10,
             y=float(r["gold_statement_30m_pct"]),
             pre=float(r["gold_pre_45m_pct"]), post=float(r["gold_post_105m_pct"]),
             vol=float(r["prior_sd60_pct"]), trend=float(r["prior_z20"]))
        for r in raw if r["eligible"].lower()=="true"]
assert len(raw)==53 and len(events)==46, (len(raw),len(events))

def avg(a): return sum(a)/len(a)
def inv(matrix):
    n=len(matrix)
    A=[list(row)+[float(j==i) for j in range(n)] for i,row in enumerate(matrix)]
    for i in range(n):
        k=max(range(i,n),key=lambda j:abs(A[j][i]))
        if abs(A[k][i])<1e-11: raise ValueError("Singular design")
        A[i],A[k]=A[k],A[i]
        v=A[i][i];A[i]=[x/v for x in A[i]]
        for j in range(n):
            if j==i: continue
            mul=A[j][i];A[j]=[x-mul*y for x,y in zip(A[j],A[i])]
    return [a[n:] for a in A]

def ols_hc3(data,design,target="y"):
    X=[design(r) for r in data]; Y=[r[target] for r in data]
    k=len(X[0]);G=[[sum(z[i]*z[j] for z in X) for j in range(k)] for i in range(k)]
    Gi=inv(G)
    xy=[sum(z[i]*v for z,v in zip(X,Y)) for i in range(k)]
    beta=[sum(g*t for g,t in zip(row,xy)) for row in Gi]
    meat=[[0.0]*k for _ in range(k)]
    for z,y in zip(X,Y):
        e=y-sum(b*v for b,v in zip(beta,z))
        h=sum(z[i]*Gi[i][j]*z[j] for i in range(k) for j in range(k))
        w=(e/max(1e-8,1-h))**2
        for i in range(k):
            for j in range(k):meat[i][j]+=w*z[i]*z[j]
    diag=[]
    for i in range(k):
        variance=sum(Gi[i][a]*meat[a][b]*Gi[b][i] for a in range(k) for b in range(k))
        diag.append(math.sqrt(max(0,variance)))
    residual=[y-sum(b*v for b,v in zip(beta,z)) for y,z in zip(Y,X)]
    rss=sum(e*e for e in residual); tss=sum((v-avg(Y))**2 for v in Y)
    return {"n":len(data),"beta":beta,"HC3_se":diag,"R2":1-rss/tss}
base=lambda r:[1,r["x"]]
a=ols_hc3(events,base); assert abs(a["beta"][1]+0.1608197349819626)<1e-9
placebo=ols_hc3(events,base,target="pre")
post=ols_hc3(events,base,target="post")
mp1=ols_hc3(events,lambda r:[1,r["mp1"]])
vol=avg([r["vol"] for r in events]);trend=avg([r["trend"] for r in events])
sv=math.sqrt(avg([(r["vol"]-vol)**2 for r in events]))
st=math.sqrt(avg([(r["trend"]-trend)**2 for r in events]))
def conditional(r):
    v=(r["vol"]-vol)/sv;t=(r["trend"]-trend)/st
    return [1,r["x"],v,t,r["x"]*v,r["x"]*t]
full=ols_hc3(events,conditional)
loyo=[{"year_excluded":y,**ols_hc3([r for r in events if r["year"]!=y],base)}
      for y in range(2020,2026)]
print(json.dumps({"sample_n":len(events),"main":a,"placebo":placebo,
    "continuation":post,"MP1_proxy":mp1,"state_interactions":full,
    "standardization":{"vol_mean":vol,"vol_sd":sv,"trend_mean":trend,"trend_sd":st},
    "leave_year_out":loyo,"caution":"Explanatory same-window association, not forward forecast or proven causal effect."},
    ensure_ascii=False,indent=2))
