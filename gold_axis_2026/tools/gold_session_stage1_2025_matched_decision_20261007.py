import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import balanced_accuracy_score,recall_score

AX=Path(__file__).resolve().parents[1]
G=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_PREDICTIONS_2026-10-07.csv"
S=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
SG=AX/"GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
W=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
B=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
OUT=AX/"SESSION_STAGE1_2025_DECISION_OUT";OUT.mkdir(exist_ok=True)
KEY=["partition","window","label_date","start_utc","y_up"]
ALLOWED_15={("SOBTI_5_ET","ASIA_MORNING_LIT")}

def metric(g):
 y=g.y_up.astype(int).to_numpy();p=g.p_up.astype(float).to_numpy();pr=(p>=.5).astype(int)
 return {"n":len(g),"accuracy":float((pr==y).mean()),"balanced_accuracy":float(balanced_accuracy_score(y,pr)),
         "up_recall":float(recall_score(y,pr,pos_label=1,zero_division=0)),
         "down_recall":float(recall_score(y,pr,pos_label=0,zero_division=0)),
         "brier":float(np.mean((p-y)**2))}

def prep(path,src):
 q=pd.read_csv(path);q["start_utc"]=pd.to_datetime(q.start_utc,utc=True);q["source"]=src
 return q

def main():
 g=prep(G,"GLOBAL");s=prep(S,"S14");sg=prep(SG,"SAGE")
 # Canonical names; keep only frozen candidates.
 allrows=[g]
 ss=s[s.model.isin(["S14_A1_PLUS_1H_FULL","S14_A1_PLUS_15M_FULL"])].copy()
 ss=ss[(ss.model!="S14_A1_PLUS_15M_FULL")|ss.apply(lambda r:(r.partition,r.window) in ALLOWED_15,axis=1)]
 allrows.append(ss)
 allrows.append(sg[sg.model.isin(["S15_SESSION_ONLY","S16_PATH_SESSION"])])
 x=pd.concat(allrows,ignore_index=True)
 # Identity audits.
 a=g[g.model=="A1_ARCR"].merge(s[s.model=="A1_DIRECT_MATCHED"],on=KEY,suffixes=("_g","_s"))
 a1diff=float((a.p_up_g-a.p_up_s).abs().max()) if len(a) else None
 p=g[g.model=="PATH_GLOBAL_1H"].merge(sg[sg.model=="S16_PATH_GLOBAL_MATCHED"],on=KEY,suffixes=("_g","_s"))
 pdiff=float((p.p_up_g-p.p_up_s).abs().max()) if len(p) else None

 # Target counts.
 tt=[]
 for path in [W,B]:
  q=pd.read_csv(path);q=q[q.final_trainable.astype(str).str.lower().eq("true")];q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
  q=q[q.start_utc.dt.year.eq(2025)];tt.append(q)
 t=pd.concat(tt,ignore_index=True)
 tcount={(a,b):len(z) for (a,b),z in t.groupby(["partition","window"])}

 decisions=[];matched_rows=[]
 for (part,win),z0 in x.groupby(["partition","window"],sort=True):
  models=sorted(z0.model.unique())
  if len(models)<2:continue
  sets=[]
  for m in models:
   q=z0[z0.model==m];sets.append(set(map(tuple,q[KEY].astype(str).to_numpy())))
  common=set.intersection(*sets)
  if not common:continue
  cdf=pd.DataFrame(list(common),columns=KEY)
  cdf["start_utc"]=pd.to_datetime(cdf.start_utc,utc=True);cdf["y_up"]=cdf.y_up.astype(int)
  rows=[]
  for m in models:
   q=z0[z0.model==m][KEY+["p_up"]].copy()
   q["y_up"]=q.y_up.astype(int)
   mm=cdf.merge(q,on=KEY,validate="one_to_one");mt=metric(mm)
   admissible=min(mt["up_recall"],mt["down_recall"])>=.30
   rows.append({"model":m,**mt,"admissible":admissible})
   matched_rows.append({"partition":part,"window":win,"model":m,**mt,"admissible":admissible})
  adm=[r for r in rows if r["admissible"]]
  winner=max(adm,key=lambda r:r["balanced_accuracy"]) if adm else None
  decisions.append({"partition":part,"window":win,"target_n":tcount.get((part,win)),
                    "common_n":len(common),"common_coverage":len(common)/tcount.get((part,win),len(common)),
                    "winner":None if winner is None else winner["model"],
                    "winner_ba":None if winner is None else winner["balanced_accuracy"],
                    "winner_brier":None if winner is None else winner["brier"],
                    "status":"NO_ADMISSIBLE_MODEL" if winner is None else "BEST_FROZEN_ON_COMMON_ROWS"})
 pd.DataFrame(matched_rows).to_csv(OUT/"matched_metrics.csv",index=False)
 pd.DataFrame(decisions).to_csv(OUT/"decisions.csv",index=False)
 out={"status":"STAGE1_2025_MATCHED_DECISION_COMPLETE","identity_audit":{"A1_max_abs_diff":a1diff,"PATH_max_abs_diff":pdiff},
      "recall_floor":0.30,"decisions":decisions,
      "interpretation":"Winners are transport winners only on the exact common frozen-candidate rows; they do not create a new fallback/router for non-common rows."}
 (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
