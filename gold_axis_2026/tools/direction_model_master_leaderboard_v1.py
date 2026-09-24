from __future__ import annotations
import argparse, importlib.util, json, math, re, sys
from collections import defaultdict
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m
    assert spec.loader is not None; spec.loader.exec_module(m); return m

def safe(a,b): return a/b if b else None

def binary_metrics(rows, pred_key):
    n=len(rows)
    tp=sum(r[pred_key]==1 and r["actual_up"]==1 for r in rows)
    fp=sum(r[pred_key]==1 and r["actual_up"]==0 for r in rows)
    tn=sum(r[pred_key]==0 and r["actual_up"]==0 for r in rows)
    fn=sum(r[pred_key]==0 and r["actual_up"]==1 for r in rows)
    au=tp+fn; ad=tn+fp
    upr=safe(tp,au); dnr=safe(tn,ad)
    return {
      "n":n,"actual_up":au,"actual_down":ad,"tp":tp,"fp":fp,"tn":tn,"fn":fn,
      "up_precision":safe(tp,tp+fp),"up_recall":upr,"false_up_fpr":safe(fp,ad),
      "down_precision":safe(tn,tn+fn),"down_recall":dnr,"false_down_fpr":safe(fn,au),
      "balanced_accuracy":(upr+dnr)/2 if upr is not None and dnr is not None else None,
      "accuracy":safe(tp+tn,n),"pred_up":tp+fp,"pred_down":tn+fn
    }

def up_only_metrics(rows,pred_key):
    n=len(rows); au=sum(r["actual_up"] for r in rows); ad=n-au
    tp=sum(r[pred_key]==1 and r["actual_up"]==1 for r in rows)
    fp=sum(r[pred_key]==1 and r["actual_up"]==0 for r in rows)
    return {
      "n":n,"actual_up":au,"actual_down":ad,"up_calls":tp+fp,"tp":tp,"fp":fp,
      "up_precision":safe(tp,tp+fp),"up_recall":safe(tp,au),"false_up_fpr":safe(fp,ad),
      "not_up_count":n-tp-fp,
      "note":"NOT-UP is abstention/context here; it is NOT scored as a positive DOWN call."
    }

def ternary_metrics(rows,key):
    n=len(rows); au=sum(r["actual_up"] for r in rows); ad=n-au
    up_calls=sum(r[key]==1 for r in rows); down_calls=sum(r[key]==-1 for r in rows); neutral=n-up_calls-down_calls
    tp=sum(r[key]==1 and r["actual_up"]==1 for r in rows)
    fp=sum(r[key]==1 and r["actual_up"]==0 for r in rows)
    td=sum(r[key]==-1 and r["actual_up"]==0 for r in rows)
    fd=sum(r[key]==-1 and r["actual_up"]==1 for r in rows)
    upr=safe(tp,au); dnr=safe(td,ad)
    active=[r for r in rows if r[key]!=0]
    active_correct=sum((r[key]==1 and r["actual_up"]==1) or (r[key]==-1 and r["actual_up"]==0) for r in active)
    return {
      "n":n,"actual_up":au,"actual_down":ad,"up_calls":up_calls,"down_calls":down_calls,"neutral":neutral,
      "true_up":tp,"false_up":fp,"true_down":td,"false_down":fd,
      "up_precision":safe(tp,up_calls),"up_recall":upr,"false_up_fpr":safe(fp,ad),
      "down_precision":safe(td,down_calls),"down_recall":dnr,"false_down_fpr":safe(fd,au),
      "balanced_accuracy_full_timeline":(upr+dnr)/2 if upr is not None and dnr is not None else None,
      "coverage":safe(len(active),n),"active_accuracy":safe(active_correct,len(active))
    }

def parse_manifest(path):
    c=path.read_text(encoding="utf-8")
    pat=re.compile(r"^###\s+(R\d+)\.\s+(.+)$",re.M)
    ms=list(pat.finditer(c)); out=[]
    labels=["METHOD / IDENTITY","ROLE","WHY TESTED","DATA / ROUTE","PRE-2025 RESULT","LOCKED 2025 RESULT","FINAL STATUS","WHY ACCEPTED / REJECTED / NOT_PROVEN"]
    for i,m in enumerate(ms):
      sec=c[m.start():ms[i+1].start() if i+1<len(ms) else len(c)]
      z={"id":m.group(1),"title":m.group(2).strip()}
      for lab in labels:
        mm=re.search(r"\*\*"+re.escape(lab)+r":\*\*\s*([^\n]+)",sec)
        if mm: z[lab.lower().replace(" / ","_").replace(" ","_").replace("-","_")]=mm.group(1).strip()
      out.append(z)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--fixed",type=Path,required=True)
    ap.add_argument("--local1",type=Path,required=True)
    ap.add_argument("--local2",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    base=load("base_leader",a.base); fixed=load("fixed_leader",a.fixed); l1=load("local1_leader",a.local1); l2=load("local2_leader",a.local2)
    base.CUTOFF="2026-09-01T04:00:00Z"
    days=base.load_days(); tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays); tmap={r["target_date"]:r for r in trows}
    bmaps=base.bonato_maps(bdays); lmaps=base.logit_maps(ldays); ctx=base.legacy_context(daily)

    allsets=[set(tmap)]
    allsets += [set(v) for v in bmaps.values()]
    allsets += [set(v) for v in lmaps.values()]
    common=sorted(set.intersection(*allsets))
    rows=[]
    for td in common:
      y=int(tmap[td]["actual_up"]); od=tmap[td]["origin_date"]
      vals=[y]
      for mp in bmaps.values(): vals.append(int(mp[td]["actual_up"]))
      for mp in lmaps.values(): vals.append(int(mp[td]["actual_up"]))
      if len(set(vals))!=1: raise RuntimeError(f"ACTUAL_MISMATCH:{td}")
      z={"origin_date":od,"target_date":td,"year":int(td[:4]),"actual_up":y,
         "TSM_signal":int(tmap[td]["tsm_signal"]),
         "TTSM_S1_signal":int(tmap[td]["ttsm_s1_signal"]),
         "TTSM_S2_signal":int(tmap[td]["ttsm_s2_signal"])}
      for name,mp in bmaps.items(): z[name]=int(mp[td]["up"])
      for name,mp in lmaps.items(): z[name]=int(mp[td]["up"])
      cc=ctx[od]
      z["FAST_UP"]=int(cc["FAST_UP"]); z["SLOW_UP"]=int(cc["SLOW_UP"]); z["MONTHLY_UP"]=int(cc["MONTHLY_UP"])
      rows.append(z)

    # Frozen Router V2 and today's router successors are evaluated on their authority row construction.
    authority_rows=fixed.build_rows(base)
    by=defaultdict(list)
    for r in authority_rows: by[r["year"]].append(r)
    r24,h24=fixed.score_router_year(base,by[2024],by[2023])
    r25,h25=fixed.score_router_year(base,by[2025],h24)
    r26,_=fixed.score_router_year(base,by[2026],h25)
    router_v2={"2024":fixed.metrics(r24),"2025":fixed.metrics(r25),"2026":fixed.metrics(r26)}

    fs=fixed.fixed_share_run(authority_rows,0.005,0.5)
    lc1=l1.local_competence_run(l1.build_rows(base),90)
    # V2 exact selected hyperparameters.
    lc2rows=l1.build_rows(base); lc2=l2.run(lc2rows,120,0.525,0.50)

    annual={}
    model_types={
      "FAST_UP":"UP_ONLY","SLOW_UP":"UP_ONLY","MONTHLY_UP":"UP_ONLY",
      "TSM":"TERNARY","TTSM_S1":"TERNARY","TTSM_S2":"TERNARY",
      "BONATO_AR1_QBOOST_H1":"BINARY","BONATO_AR1_RM_QBOOST_H1":"BINARY",
      "AR1_LOGIT":"BINARY","RV_LOGIT":"BINARY","RSK_LOGIT":"BINARY","RM_LOGIT":"BINARY","AR1_RM_LOGIT":"BINARY"
    }
    for y in [2023,2024,2025,2026]:
      yy=[r for r in rows if r["year"]==y]
      annual[str(y)]={}
      for name,typ in model_types.items():
        if typ=="UP_ONLY": m=up_only_metrics(yy,name)
        elif typ=="TERNARY": m=ternary_metrics(yy,name+"_signal")
        else: m=binary_metrics(yy,name)
        annual[str(y)][name]={"output_type":typ,"metrics":m}

    successor={
      "ROUTER_V2":{"2024":router_v2["2024"],"2025":router_v2["2025"],"2026":router_v2["2026"]},
      "FIXED_SHARE_V1":{},
      "LOCAL_COMPETENCE_V1":{},
      "LOCAL_COMPETENCE_V2":{}
    }
    for y in [2024,2025,2026]:
      successor["FIXED_SHARE_V1"][str(y)]=fixed.metrics([r for r in fs if r["year"]==y])
      successor["LOCAL_COMPETENCE_V1"][str(y)]=l1.metrics([r for r in lc1 if r["year"]==y])
      successor["LOCAL_COMPETENCE_V2"][str(y)]=l2.metrics([r for r in lc2 if r["year"]==y])

    inv=parse_manifest(a.manifest)
    r_count=sum(x["id"].startswith("R") for x in inv)
    h_count=sum(x["id"].startswith("H") for x in inv)
    if (r_count,h_count)!=(57,37): raise RuntimeError(f"MANIFEST_INVENTORY_COUNT:R={r_count}:H={h_count}")

    result={
      "identity":"GOLD_CONTROL_DIRECTION_MODEL_MASTER_LEADERBOARD_V1_RESEARCH",
      "date":"2026-09-24",
      "manifest_inventory_count":len(inv),
      "manifest_r_count":r_count,
      "manifest_h_count":h_count,
      "manifest_inventory":inv,
      "post_manifest_research_models":[
        "GOLD_CONTROL_DYNAMIC_FIXED_SHARE_ROUTER_V1_RESEARCH",
        "GOLD_CONTROL_DYNAMIC_LOCAL_COMPETENCE_ROUTER_V1_RESEARCH",
        "GOLD_CONTROL_DYNAMIC_LOCAL_COMPETENCE_ROUTER_V2_RESEARCH",
        "DEFAULT_GOLD_DOWN_EXIT_LOGIT_V1_RESEARCH",
        "DEFAULT_GOLD_DOWN_EXIT_LOGIT_V2_RESEARCH"
      ],
      "same_clock_common_daily":{
        "row_count":len(rows),
        "first_target":rows[0]["target_date"],"last_target":rows[-1]["target_date"],
        "model_types":model_types,
        "annual":annual
      },
      "successor_routers":successor,
      "interpretation_contract":{
        "binary":"UP and DOWN are both explicit complements; TP/FP/TN/FN and balanced accuracy are valid binary direction diagnostics.",
        "ternary":"Only +1 and -1 are explicit direction calls; neutral is not silently converted to DOWN. Full-timeline class recalls count neutral as missed direction.",
        "up_only":"NOT-UP is abstention/context, never positive DOWN. Only UP precision/recall/FPR are reported."
      },
      "governance":{"random_split":False,"2025_retuned":False,"2026_retuned":False,"database_write":False,"runtime_promotion":False,"canonical_branch_modified":False}
    }
    p=a.out/"GOLD_CONTROL_DIRECTION_MODEL_MASTER_LEADERBOARD_V1_RESULT_2026-09-24.json"
    p.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"identity":result["identity"],"manifest_inventory_count":len(inv),"manifest_r_count":r_count,"manifest_h_count":h_count,"same_clock_n":len(rows),"annual":annual,"successor_routers":successor},indent=2))

if __name__=="__main__": main()
