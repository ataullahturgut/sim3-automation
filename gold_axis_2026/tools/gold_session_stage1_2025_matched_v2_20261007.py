import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import balanced_accuracy_score,recall_score

AX=Path(__file__).resolve().parents[1]
G=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
S=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
SG=AX/"GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
W=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
B=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"
OUT=AX/"SESSION_STAGE1_2025_MATCHED_V2_OUT";OUT.mkdir(exist_ok=True)
KEY=["partition","window","label_date","start_utc","y_up"]

def met(g):
 y=g.y_up.astype(int).to_numpy();p=g.p_up.astype(float).to_numpy();pr=(p>=.5).astype(int)
 return {"n":len(g),"accuracy":float((pr==y).mean()),"balanced_accuracy":float(balanced_accuracy_score(y,pr)),
         "up_recall":float(recall_score(y,pr,pos_label=1,zero_division=0)),
         "down_recall":float(recall_score(y,pr,pos_label=0,zero_division=0)),
         "brier":float(np.mean((p-y)**2))}

def load(p):
 q=pd.read_csv(p);q["start_utc"]=pd.to_datetime(q.start_utc,utc=True).astype(str);return q

def main():
 g=load(G);s=load(S);sg=load(SG)
 x=[g]
 q=s[s.model.isin(["S14_A1_PLUS_1H_FULL","S14_A1_PLUS_15M_FULL"])].copy()
 q=q[(q.model!="S14_A1_PLUS_15M_FULL")|((q.partition=="SOBTI_5_ET")&(q.window=="ASIA_MORNING_LIT"))]
 x.append(q)
 x.append(sg[sg.model.isin(["S15_SESSION_ONLY","S16_PATH_SESSION"])])
 x=pd.concat(x,ignore_index=True)

 tt=[]
 for p in [W,B]:
  q=pd.read_csv(p);q=q[q.final_trainable.astype(str).str.lower().eq("true")];q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
  tt.append(q[q.start_utc.dt.year.eq(2025)])
 t=pd.concat(tt,ignore_index=True)
 counts={(a,b):len(z) for (a,b),z in t.groupby(["partition","window"])}

 rows=[];dec=[]
 for (part,win),z in x.groupby(["partition","window"],sort=True):
  mods=sorted(z.model.unique())
  sets=[set(map(tuple,z[z.model.eq(m)][KEY].astype(str).to_numpy())) for m in mods]
  common=set.intersection(*sets)
  if not common:continue
  c=pd.DataFrame(list(common),columns=KEY);c["y_up"]=c.y_up.astype(int)
  rr=[]
  for m in mods:
   q=z[z.model.eq(m)][KEY+["p_up"]].copy();q["y_up"]=q.y_up.astype(int)
   mm=c.merge(q,on=KEY,validate="one_to_one");r=met(mm)
   r.update({"partition":part,"window":win,"model":m,"admissible":min(r["up_recall"],r["down_recall"])>=.30})
   rr.append(r);rows.append(r)
  adm=[r for r in rr if r["admissible"]]
  if not adm:
   dec.append({"partition":part,"window":win,"target_n":counts[(part,win)],"common_n":len(common),
               "coverage":len(common)/counts[(part,win)],"winner":None,"winner_ba":None,"status":"NO_ADMISSIBLE_MODEL"})
  else:
   w=max(adm,key=lambda r:(r["balanced_accuracy"],-r["brier"]))
   status="PROMOTABLE_TRANSPORT_WINNER" if w["balanced_accuracy"]>=.50 else "BEST_BUT_BELOW_50_BA"
   dec.append({"partition":part,"window":win,"target_n":counts[(part,win)],"common_n":len(common),
               "coverage":len(common)/counts[(part,win)],"winner":w["model"],"winner_ba":w["balanced_accuracy"],
               "winner_brier":w["brier"],"status":status})
 pd.DataFrame(rows).to_csv(OUT/"matched_metrics.csv",index=False)
 pd.DataFrame(dec).to_csv(OUT/"decisions.csv",index=False)
 out={"status":"STAGE1_2025_MATCHED_V2_COMPLETE","recall_floor":0.30,
      "decision_rule":"highest balanced accuracy among frozen candidates on exact common rows; Brier only breaks exact BA tie; winner below 50% BA is not promoted",
      "decisions":dec}
 (OUT/"summary.json").write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
